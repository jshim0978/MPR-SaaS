"""
Baseline 3: Chain-of-Thought (CoT)

Append CoT trigger to prompt:
"{prompt}\n\nLet's break this down step by step:"

Tests if CoT prompting reduces hallucinations.
"""

import time
import tiktoken
from typing import Dict

class CoTBaseline:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.cot_suffix = "\n\nLet's break this down step by step:"
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))
    
    def refine(self, prompt: str) -> Dict:
        """
        Apply Chain-of-Thought trigger
        
        Returns:
            refined_prompt: Prompt with CoT suffix
            latency_ms: Negligible
            tokens: New token count
        """
        t0 = time.perf_counter()
        
        # Append CoT trigger
        refined_prompt = prompt + self.cot_suffix
        
        latency_ms = (time.perf_counter() - t0) * 1000.0
        
        original_tokens = self.count_tokens(prompt)
        refined_tokens = self.count_tokens(refined_prompt)
        
        return {
            "method": "cot",
            "original_prompt": prompt,
            "refined_prompt": refined_prompt,
            "refinement_latency_ms": latency_ms,
            "prompt_tokens": refined_tokens,
            "refinement_tokens_added": refined_tokens - original_tokens,
            "metadata": {
                "cot_trigger": self.cot_suffix,
                "description": "Chain-of-thought prompting"
            }
        }
    
    def __str__(self):
        return "Chain-of-Thought (CoT)"


if __name__ == "__main__":
    baseline = CoTBaseline()
    
    test_prompts = [
        "what is the captial of frane?",
        "tell me about quantom physics",
        "how does photosythesis work",
    ]
    
    print("="*80)
    print("CHAIN-OF-THOUGHT BASELINE TEST")
    print("="*80)
    
    for prompt in test_prompts:
        print(f"\nOriginal: {prompt}")
        result = baseline.refine(prompt)
        print(f"Refined:  {result['refined_prompt']}")
        print(f"Latency:  {result['refinement_latency_ms']:.3f}ms")
        print(f"Tokens:   {result['prompt_tokens']}")
        print(f"Added:    {result['refinement_tokens_added']}")

