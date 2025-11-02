"""
Baseline 2: Simple Template

Apply basic template-based refinement:
"Please clarify and correct: {prompt}"

Minimal overhead, tests if simple prompting helps.
"""

import time
import tiktoken
from typing import Dict

class TemplateBaseline:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.template = "Please clarify and correct: {prompt}"
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))
    
    def refine(self, prompt: str) -> Dict:
        """
        Apply simple template refinement
        
        Returns:
            refined_prompt: Template-wrapped prompt
            latency_ms: Template formatting time
            tokens: New token count
        """
        t0 = time.perf_counter()
        
        # Apply template
        refined_prompt = self.template.format(prompt=prompt)
        
        latency_ms = (time.perf_counter() - t0) * 1000.0
        
        original_tokens = self.count_tokens(prompt)
        refined_tokens = self.count_tokens(refined_prompt)
        
        return {
            "method": "template",
            "original_prompt": prompt,
            "refined_prompt": refined_prompt,
            "refinement_latency_ms": latency_ms,
            "prompt_tokens": refined_tokens,
            "refinement_tokens_added": refined_tokens - original_tokens,
            "metadata": {
                "template": self.template,
                "description": "Simple template-based refinement"
            }
        }
    
    def __str__(self):
        return "Simple Template"


if __name__ == "__main__":
    baseline = TemplateBaseline()
    
    test_prompts = [
        "what is the captial of frane?",
        "tell me about quantom physics",
        "how does photosythesis work",
    ]
    
    print("="*80)
    print("TEMPLATE BASELINE TEST")
    print("="*80)
    
    for prompt in test_prompts:
        print(f"\nOriginal: {prompt}")
        result = baseline.refine(prompt)
        print(f"Refined:  {result['refined_prompt']}")
        print(f"Latency:  {result['refinement_latency_ms']:.3f}ms")
        print(f"Tokens:   {result['prompt_tokens']}")
        print(f"Added:    {result['refinement_tokens_added']}")

