"""
Baseline 3: CoT (Chain-of-Thought)

Appends chain-of-thought instruction to prompt.
"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'frameworks'))
from base import StandardizedMethod, RefinementResult

class CoTBaseline(StandardizedMethod):
    def __init__(self):
        super().__init__(name="CoT")
        self.cot_suffix = "\n\nLet's approach this step by step:"
    
    def refine(self, prompt: str) -> RefinementResult:
        """Append CoT suffix"""
        t0 = time.perf_counter()
        refined_prompt = prompt + self.cot_suffix
        latency_ms = (time.perf_counter() - t0) * 1000.0
        
        original_tokens = len(prompt.split())
        refined_tokens = len(refined_prompt.split())
        
        return RefinementResult(
            method_name=self.name,
            original_prompt=prompt,
            refined_prompt=refined_prompt,
            latency_ms=latency_ms,
            tokens_used=refined_tokens,
            metadata={"cot_suffix": self.cot_suffix, "tokens_added": refined_tokens - original_tokens}
        )
    
    def get_cost_per_token(self):
        return {"input": 0.0, "output": 0.0}


if __name__ == "__main__":
    cot = CoTBaseline()
    test_prompt = "what is the capital of France?"
    result = cot.refine(test_prompt)
    print(f"Original: {result.original_prompt}")
    print(f"Refined:  {result.refined_prompt}")
    print(f"Latency:  {result.latency_ms:.3f}ms")
    print(f"Tokens:   {result.tokens_used}")
