"""
CoVe (Chain-of-Verification) - Dhuliawala et al., 2023

Reference: "Chain-of-Verification Reduces Hallucination in Large Language Models"
Paper: https://arxiv.org/abs/2309.11495
Meta AI Research

Core idea: Generate → Verify → Revise
1. Generate initial response
2. Generate verification questions
3. Answer verification questions independently
4. Revise original response based on verification

Simplified implementation for comparison framework.
"""

import os
import time
from typing import Dict, List
import sys
sys.path.append('/home/comparison/frameworks')
from base import StandardizedMethod, RefinementResult

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class CoVe(StandardizedMethod):
    """
    Chain-of-Verification - Reduces hallucination via verification loop
    
    Process:
    1. Generate baseline response
    2. Plan verification questions
    3. Answer questions independently
    4. Generate final verified response
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(name="CoVe")
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package required for CoVe")
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def generate_verifications(self, prompt: str, baseline_response: str) -> List[str]:
        """Generate verification questions for the baseline response"""
        verification_prompt = f"""Given this question and response, generate 2-3 verification questions to check factual accuracy:

Question: {prompt}
Response: {baseline_response}

Generate specific verification questions that can independently confirm or refute claims in the response.
Output only the questions, one per line."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": verification_prompt}],
                temperature=0.3,
                max_tokens=200
            )
            questions = response.choices[0].message.content.strip().split('\n')
            return [q.strip() for q in questions if q.strip()][:3]  # Max 3
        except:
            return []
    
    def answer_verification(self, question: str) -> str:
        """Answer verification question independently"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": question}],
                temperature=0.0,  # Factual
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except:
            return ""
    
    def refine(self, prompt: str) -> RefinementResult:
        """Chain-of-Verification refinement"""
        t0 = time.perf_counter()
        total_tokens = 0
        
        try:
            # Step 1: Generate baseline response
            baseline_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            baseline_text = baseline_response.choices[0].message.content.strip()
            total_tokens += baseline_response.usage.total_tokens
            
            # Step 2: Generate verification questions
            verification_questions = self.generate_verifications(prompt, baseline_text)
            total_tokens += 100  # Estimate
            
            if not verification_questions:
                # Fallback if no questions generated
                latency_ms = (time.perf_counter() - t0) * 1000.0
                return RefinementResult(
                    method_name=self.name,
                    original_prompt=prompt,
                    refined_prompt=baseline_text,
                    latency_ms=latency_ms,
                    tokens_used=total_tokens,
                    metadata={"stage": "baseline_only", "verifications": 0}
                )
            
            # Step 3: Answer verification questions independently
            verifications = []
            for q in verification_questions:
                answer = self.answer_verification(q)
                verifications.append({"question": q, "answer": answer})
                total_tokens += 80  # Estimate
            
            # Step 4: Generate final verified response
            final_prompt = f"""Original question: {prompt}

Initial response: {baseline_text}

Verification results:
{chr(10).join(f"Q: {v['question']}\nA: {v['answer']}" for v in verifications)}

Based on the verifications, provide a corrected and verified final response to the original question.
Output only the final response."""
            
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": final_prompt}],
                temperature=0.3,
                max_tokens=250
            )
            refined_prompt = final_response.choices[0].message.content.strip()
            total_tokens += final_response.usage.total_tokens
            
            latency_ms = (time.perf_counter() - t0) * 1000.0
            
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=refined_prompt,
                latency_ms=latency_ms,
                tokens_used=total_tokens,
                metadata={
                    "baseline_response": baseline_text,
                    "verifications": verifications,
                    "num_verifications": len(verifications),
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
                tokens_used=total_tokens,
                metadata={},
                error=str(e)
            )
    
    def get_cost_per_token(self) -> Dict[str, float]:
        """Cost for GPT-4o (multiple calls)"""
        return {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000}


if __name__ == "__main__":
    print("="*80)
    print("CoVe (Chain-of-Verification) Test")
    print("="*80)
    
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI not available. Install with: pip install openai")
        exit(1)
    
    try:
        cove = CoVe()
        
        prompt = "What is the capital of France and when was it founded?"
        print(f"\n📝 Prompt: {prompt}")
        result = cove.refine(prompt)
        
        if result.error:
            print(f"   ERROR: {result.error}")
        else:
            print(f"\n✅ Refined Response: {result.refined_prompt}")
            print(f"\n📊 Metadata:")
            print(f"   Baseline: {result.metadata.get('baseline_response', 'N/A')[:60]}...")
            print(f"   Verifications: {result.metadata.get('num_verifications', 0)}")
            print(f"   Latency: {result.latency_ms:.1f}ms")
            print(f"   Tokens: {result.tokens_used}")
            print(f"   Cost: ${cove.calculate_cost(result.tokens_used):.6f}")
    
    except ValueError as e:
        print(f"\n❌ {e}")
        print("Set OPENAI_API_KEY environment variable to test")

