"""
Baseline 2: Template (Simple Wrapper)

Wraps the prompt with a clarifying instruction template.
"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'frameworks'))
from base import StandardizedMethod, RefinementResult

class TemplateBaseline(StandardizedMethod):
    def __init__(self):
        super().__init__(name="Template")
        self.template = "Please provide a clear and accurate answer to: {prompt}"
    
    def refine(self, prompt: str) -> RefinementResult:
        """Wrap prompt in template"""
        t0 = time.perf_counter()
        refined_prompt = self.template.format(prompt=prompt)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        
        original_tokens = len(prompt.split())
        refined_tokens = len(refined_prompt.split())
        
        return RefinementResult(
            method_name=self.name,
            original_prompt=prompt,
            refined_prompt=refined_prompt,
            latency_ms=latency_ms,
            tokens_used=refined_tokens,
            metadata={"template": self.template, "tokens_added": refined_tokens - original_tokens}
        )
    
    def get_cost_per_token(self):
        return {"input": 0.0, "output": 0.0}


if __name__ == "__main__":
    template = TemplateBaseline()
    test_prompt = "what is the capital of France?"
    result = template.refine(test_prompt)
    print(f"Original: {result.original_prompt}")
    print(f"Refined:  {result.refined_prompt}")
    print(f"Latency:  {result.latency_ms:.3f}ms")
    print(f"Tokens:   {result.tokens_used}")
