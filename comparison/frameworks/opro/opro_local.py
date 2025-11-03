"""
OPRO (1-iteration) - Local Llama Version

Uses Llama-3.2-3B or Llama-3.1-8B as meta-optimizer.
Compatible with vLLM inference server.
"""

import os
import time
import sys
# Add /home to path to import mpr package
sys.path.insert(0, '/home')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base import BasePromptOptimizer, RefinementResult
from mpr.common.vllm_client import chat


class OPRO_Local(BasePromptOptimizer):
    """
    OPRO using local Llama models via vLLM
    
    Compares Llama-3.2-3B vs Llama-3.1-8B as meta-optimizers
    """
    
    def __init__(self, model_size: str = "3b"):
        """
        Args:
            model_size: "3b" for Llama-3.2-3B or "8b" for Llama-3.1-8B
        """
        self.model_size = model_size.lower()
        if self.model_size == "3b":
            model_name = "Llama-3.2-3B"
            os.environ["MODEL_NAME"] = "meta-llama/Llama-3.2-3B-Instruct"
        elif self.model_size == "8b":
            model_name = "Llama-3.1-8B"
            os.environ["MODEL_NAME"] = "meta-llama/Llama-3.1-8B-Instruct"
        else:
            raise ValueError(f"Invalid model_size: {model_size}. Use '3b' or '8b'")
        
        super().__init__(name=f"OPRO_Local_{model_name}", model=model_name, max_iterations=1)
        
        self.system_prompt = (
            "You are an automatic prompt optimizer. Your task is to refine a given prompt "
            "to make it more effective for a target LLM to answer accurately and without hallucinations. "
            "You will receive an original prompt. Your output should be ONLY the optimized prompt. "
            "Do not include any conversational filler or explanations. Focus on clarity, specificity, "
            "and hallucination mitigation. Perform only ONE iteration of optimization."
        )
    
    async def refine(self, prompt: str) -> RefinementResult:
        """Single-pass meta-optimization using local Llama model"""
        t0 = time.perf_counter()
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]
        
        try:
            response = await chat(messages, temperature=0.7, max_tokens=256)
            refined_prompt = response["text"]
            latency_ms = response["latency_ms"]
            
            # Estimate tokens (vLLM doesn't return token counts in basic mode)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(refined_prompt.split()) * 1.3
            total_tokens = int(input_tokens + output_tokens)
            
        except Exception as e:
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=prompt,
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                tokens_used=len(prompt.split()),
                metadata={},
                error=f"vLLM Error: {e}"
            )
        
        end_time = time.perf_counter()
        total_latency_ms = (end_time - t0) * 1000.0
        
        return RefinementResult(
            method_name=self.name,
            original_prompt=prompt,
            refined_prompt=refined_prompt,
            latency_ms=total_latency_ms,
            tokens_used=total_tokens,
            metadata={
                "optimizer_model": self.model,
                "model_size": self.model_size,
                "vllm_latency_ms": latency_ms,
                "estimated_tokens": total_tokens
            }
        )
    
    def get_cost_per_token(self):
        """Local models: essentially free (compute cost only)"""
        # Use pricing from config/prices.yml for local models
        if self.model_size == "8b":
            return {"input": 0.10 / 1_000_000, "output": 0.20 / 1_000_000}
        else:  # 3b
            return {"input": 0.05 / 1_000_000, "output": 0.10 / 1_000_000}


if __name__ == "__main__":
    import asyncio
    
    print("="*80)
    print("OPRO Local (Llama Models) Test")
    print("="*80)
    print("Requires: vLLM server running on localhost:8001")
    print("="*80)
    
    async def main():
        test_prompts = [
            "what is the captial of frane?",
            "tell me about quantom physics",
        ]
        
        for model_size in ["3b", "8b"]:
            print(f"\n{'='*80}")
            print(f"Testing with Llama-{model_size.upper()}")
            print(f"{'='*80}")
            
            try:
                opro = OPRO_Local(model_size=model_size)
                
                for prompt in test_prompts:
                    print(f"\nOriginal: {prompt}")
                    result = await opro.refine(prompt)
                    
                    if result.error:
                        print(f"ERROR: {result.error}")
                    else:
                        print(f"Refined: {result.refined_prompt}")
                        print(f"Latency: {result.latency_ms:.1f}ms")
                        print(f"Tokens: {result.tokens_used}")
                        print(f"Cost: ${opro.calculate_cost(result.tokens_used):.6f}")
            
            except Exception as e:
                print(f"ERROR: {e}")
    
    asyncio.run(main())

