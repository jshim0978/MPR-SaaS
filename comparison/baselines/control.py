"""
Baseline 1: Control (No Refinement)

Direct prompting to target LLM with no modifications.
Establishes baseline cost, latency, and quality metrics.
"""

import time
import tiktoken
from typing import Dict

class ControlBaseline:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4/Llama tokenizer proxy
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoder.encode(text))
    
    def refine(self, prompt: str) -> Dict:
        """
        Control: No refinement, just passthrough
        
        Returns:
            refined_prompt: Same as input
            latency_ms: Negligible (just measurement overhead)
            tokens: Original prompt tokens
        """
        t0 = time.perf_counter()
        
        # No actual refinement - just passthrough
        refined_prompt = prompt
        
        latency_ms = (time.perf_counter() - t0) * 1000.0
        
        return {
            "method": "control",
            "original_prompt": prompt,
            "refined_prompt": refined_prompt,
            "refinement_latency_ms": latency_ms,
            "prompt_tokens": self.count_tokens(prompt),
            "refinement_tokens_added": 0,
            "metadata": {
                "description": "No refinement applied (control baseline)"
            }
        }
    
    def __str__(self):
        return "Control (No Refinement)"


if __name__ == "__main__":
    baseline = ControlBaseline()
    
    test_prompts = [
        "what is the captial of frane?",
        "tell me about quantom physics",
        "how does photosythesis work",
    ]
    
    print("="*80)
    print("CONTROL BASELINE TEST")
    print("="*80)
    
    for prompt in test_prompts:
        print(f"\nOriginal: {prompt}")
        result = baseline.refine(prompt)
        print(f"Refined:  {result['refined_prompt']}")
        print(f"Latency:  {result['refinement_latency_ms']:.3f}ms")
        print(f"Tokens:   {result['prompt_tokens']}")
        print(f"Added:    {result['refinement_tokens_added']}")

