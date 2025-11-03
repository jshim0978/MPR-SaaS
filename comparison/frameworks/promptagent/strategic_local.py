"""
PromptAgent (1-pass) - Local Llama Version

Strategic planning using Llama-3.2-3B or Llama-3.1-8B.
"""

import os
import time
import sys
sys.path.insert(0, '/home')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base import BasePromptOptimizer, RefinementResult
from mpr.common.vllm_client import chat


class PromptAgent_Local(BasePromptOptimizer):
    """
    PromptAgent using local Llama models via vLLM
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
        
        super().__init__(name=f"PromptAgent_Local_{model_name}", model=model_name, max_iterations=1)
        
        self.planning_prompt = """You are a strategic prompt optimization agent. Analyze this prompt and create an improvement plan:

Prompt: {prompt}

Strategic Analysis:
1. Identify issues (typos, ambiguity, missing context, vague requests)
2. Plan improvements (what to fix, what to add, what to clarify)
3. Execute improvements

Output ONLY the improved prompt, incorporating all planned improvements."""
    
    async def refine(self, prompt: str) -> RefinementResult:
        """Single-pass strategic planning"""
        t0 = time.perf_counter()
        
        planning_instruction = self.planning_prompt.format(prompt=prompt)
        messages = [
            {"role": "system", "content": "You are a strategic prompt optimization expert."},
            {"role": "user", "content": planning_instruction}
        ]
        
        try:
            response = await chat(messages, temperature=0.5, max_tokens=400)
            refined_prompt = response["text"]
            latency_ms = response["latency_ms"]
            
            input_tokens = len(prompt.split()) * 1.3
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
        
        total_latency_ms = (time.perf_counter() - t0) * 1000.0
        
        return RefinementResult(
            method_name=self.name,
            original_prompt=prompt,
            refined_prompt=refined_prompt,
            latency_ms=total_latency_ms,
            tokens_used=total_tokens,
            metadata={
                "model": self.model,
                "model_size": self.model_size,
                "approach": "strategic_planning",
                "vllm_latency_ms": latency_ms
            }
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
        print("PromptAgent Local Test")
        print("="*80)
        
        for model_size in ["3b", "8b"]:
            print(f"\n--- Llama-{model_size.upper()} ---")
            agent = PromptAgent_Local(model_size=model_size)
            
            prompt = "what is the captial of frane?"
            result = await agent.refine(prompt)
            
            if not result.error:
                print(f"Refined: {result.refined_prompt}")
                print(f"Latency: {result.latency_ms:.1f}ms")
                print(f"Cost: ${agent.calculate_cost(result.tokens_used):.6f}")
    
    asyncio.run(main())

