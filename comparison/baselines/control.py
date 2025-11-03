"""
Baseline 1: Control (No Refinement)

Direct prompting to target LLM with no modifications.
Establishes baseline cost, latency, and quality metrics.
"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'frameworks'))
from base import StandardizedMethod, RefinementResult

class ControlBaseline(StandardizedMethod):
    def __init__(self):
        super().__init__(name="Control")
    
    def refine(self, prompt: str) -> RefinementResult:
        """Control: No refinement, just passthrough"""
        t0 = time.perf_counter()
        refined_prompt = prompt
        latency_ms = (time.perf_counter() - t0) * 1000.0
        tokens = len(prompt.split())
        
        return RefinementResult(
            method_name=self.name,
            original_prompt=prompt,
            refined_prompt=refined_prompt,
            latency_ms=latency_ms,
            tokens_used=tokens,
            metadata={"no_refinement": True}
        )
    
    def get_cost_per_token(self):
        return {"input": 0.0, "output": 0.0}


if __name__ == "__main__":
    control = ControlBaseline()
    test_prompt = "what is the capital of France?"
    result = control.refine(test_prompt)
    print(f"Original: {result.original_prompt}")
    print(f"Refined:  {result.refined_prompt}")
    print(f"Latency:  {result.latency_ms:.3f}ms")
    print(f"Tokens:   {result.tokens_used}")
