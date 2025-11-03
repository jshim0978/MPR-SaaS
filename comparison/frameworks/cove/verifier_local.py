"""
CoVe (Chain-of-Verification) - Local Llama Version

Verification-based refinement using local Llama models.
"""

import os
import time
import sys
sys.path.insert(0, '/home')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base import StandardizedMethod, RefinementResult
from mpr.common.vllm_client import chat


class CoVe_Local(StandardizedMethod):
    """
    CoVe using local Llama models via vLLM
    """
    
    def __init__(self, model_size: str = "3b"):
        self.model_size = model_size.lower()
        if self.model_size == "3b":
            model_name = "Llama-3.2-3B"
            os.environ["MODEL_NAME"] = "meta-llama/Llama-3.2-3B-Instruct"
        elif self.model_size == "8b":
            model_name = "Llama-3.1-8B"
            os.environ["MODEL_NAME"] = "meta-llama/Llama-3.1-8B-Instruct"
        else:
            raise ValueError(f"Invalid model_size: {model_size}")
        
        super().__init__(name=f"CoVe_Local_{model_name}")
        self.model_name = model_name
    
    async def generate_verifications(self, prompt: str, baseline_response: str):
        """Generate verification questions"""
        verification_prompt = f"""Given this question and response, generate 2-3 verification questions to check factual accuracy:

Question: {prompt}
Response: {baseline_response}

Generate specific verification questions that can independently confirm or refute claims in the response.
Output only the questions, one per line."""
        
        try:
            response = await chat([{"role": "user", "content": verification_prompt}], temperature=0.3, max_tokens=200)
            questions = response["text"].strip().split('\n')
            return [q.strip() for q in questions if q.strip()][:3]
        except:
            return []
    
    async def answer_verification(self, question: str):
        """Answer verification question independently"""
        try:
            response = await chat([{"role": "user", "content": question}], temperature=0.0, max_tokens=100)
            return response["text"].strip()
        except:
            return ""
    
    async def refine(self, prompt: str) -> RefinementResult:
        """Chain-of-Verification refinement"""
        t0 = time.perf_counter()
        total_tokens = 0
        
        try:
            # Step 1: Generate baseline response
            baseline_response_data = await chat([{"role": "user", "content": prompt}], temperature=0.7, max_tokens=200)
            baseline_text = baseline_response_data["text"]
            total_tokens += len(prompt.split()) * 1.3 + len(baseline_text.split()) * 1.3
            
            # Step 2: Generate verification questions
            verification_questions = await self.generate_verifications(prompt, baseline_text)
            total_tokens += 100  # Estimate
            
            if not verification_questions:
                latency_ms = (time.perf_counter() - t0) * 1000.0
                return RefinementResult(
                    method_name=self.name,
                    original_prompt=prompt,
                    refined_prompt=baseline_text,
                    latency_ms=latency_ms,
                    tokens_used=int(total_tokens),
                    metadata={"stage": "baseline_only", "verifications": 0, "model_size": self.model_size}
                )
            
            # Step 3: Answer verification questions
            verifications = []
            for q in verification_questions:
                answer = await self.answer_verification(q)
                verifications.append({"question": q, "answer": answer})
                total_tokens += 80
            
            # Step 4: Generate final verified response
            final_prompt = f"""Original question: {prompt}

Initial response: {baseline_text}

Verification results:
{chr(10).join(f"Q: {v['question']}\nA: {v['answer']}" for v in verifications)}

Based on the verifications, provide a corrected and verified final response to the original question.
Output only the final response."""
            
            final_response_data = await chat([{"role": "user", "content": final_prompt}], temperature=0.3, max_tokens=250)
            refined_prompt = final_response_data["text"]
            total_tokens += len(final_prompt.split()) * 1.3 + len(refined_prompt.split()) * 1.3
            
            latency_ms = (time.perf_counter() - t0) * 1000.0
            
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=refined_prompt,
                latency_ms=latency_ms,
                tokens_used=int(total_tokens),
                metadata={
                    "baseline_response": baseline_text,
                    "verifications": verifications,
                    "num_verifications": len(verifications),
                    "model_size": self.model_size,
                    "stages": "generate→verify→revise"
                }
            )
        
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=prompt,
                latency_ms=latency_ms,
                tokens_used=int(total_tokens),
                metadata={},
                error=f"vLLM Error: {e}"
            )
    
    def get_cost_per_token(self):
        if self.model_size == "8b":
            return {"input": 0.10 / 1_000_000, "output": 0.20 / 1_000_000}
        else:
            return {"input": 0.05 / 1_000_000, "output": 0.10 / 1_000_000}


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("="*80)
        print("CoVe Local Test")
        print("="*80)
        
        for model_size in ["3b", "8b"]:
            print(f"\n--- Llama-{model_size.upper()} ---")
            cove = CoVe_Local(model_size=model_size)
            
            prompt = "What is the capital of France?"
            result = await cove.refine(prompt)
            
            if not result.error:
                print(f"Refined: {result.refined_prompt[:100]}...")
                print(f"Latency: {result.latency_ms:.1f}ms")
                print(f"Verifications: {result.metadata.get('num_verifications', 0)}")
    
    asyncio.run(main())

