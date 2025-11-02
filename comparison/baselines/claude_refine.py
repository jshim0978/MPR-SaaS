"""
Baseline 5: Claude 3.5 Refinement

Use Claude 3.5 Sonnet to refine prompts.
Alternative to GPT-4 for comparison.
"""

import time
import os
from typing import Dict
import tiktoken

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: Anthropic not installed. Install with: pip install anthropic")


class ClaudeRefineBaseline:
    def __init__(self, api_key: str = None):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not available")
        
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        self.client = Anthropic(api_key=self.api_key)
        self.encoder = tiktoken.get_encoding("cl100k_base")  # Proxy for Claude tokens
        
        self.system_prompt = (
            "You are a prompt refinement assistant. Your task is to improve user prompts by:\n"
            "1. Correcting spelling and grammar errors\n"
            "2. Clarifying ambiguous wording\n"
            "3. Adding helpful context without changing the original intent\n"
            "4. Making the prompt more specific and answerable\n\n"
            "Output ONLY the refined prompt, with no explanations or additional text."
        )
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))
    
    def refine(self, prompt: str) -> Dict:
        """
        Use Claude 3.5 Sonnet to refine the prompt
        
        Returns:
            refined_prompt: Claude-improved version
            latency_ms: API call latency
            tokens: Token counts for cost calculation
        """
        t0 = time.perf_counter()
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                temperature=0.3,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            refined_prompt = response.content[0].text.strip()
            
            # Token usage from API
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            latency_ms = (time.perf_counter() - t0) * 1000.0
            
            return {
                "method": "claude_refine",
                "original_prompt": prompt,
                "refined_prompt": refined_prompt,
                "refinement_latency_ms": latency_ms,
                "prompt_tokens": self.count_tokens(refined_prompt),
                "refinement_tokens_added": self.count_tokens(refined_prompt) - self.count_tokens(prompt),
                "refinement_input_tokens": input_tokens,
                "refinement_output_tokens": output_tokens,
                "metadata": {
                    "model": "claude-3-5-sonnet-20241022",
                    "temperature": 0.3,
                    "description": "Claude 3.5 Sonnet-based prompt refinement"
                }
            }
        
        except Exception as e:
            # Fallback to passthrough on error
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return {
                "method": "claude_refine",
                "original_prompt": prompt,
                "refined_prompt": prompt,  # Fallback
                "refinement_latency_ms": latency_ms,
                "prompt_tokens": self.count_tokens(prompt),
                "refinement_tokens_added": 0,
                "error": str(e),
                "metadata": {
                    "description": "Claude refinement failed, using original prompt"
                }
            }
    
    def __str__(self):
        return "Claude 3.5 Refinement"


if __name__ == "__main__":
    if not ANTHROPIC_AVAILABLE:
        print("Anthropic not available. Install with: pip install anthropic")
        exit(1)
    
    baseline = ClaudeRefineBaseline()
    
    test_prompts = [
        "what is the captial of frane?",
        "tell me about quantom physics",
        "how does photosythesis work",
    ]
    
    print("="*80)
    print("CLAUDE 3.5 REFINEMENT BASELINE TEST")
    print("="*80)
    
    for prompt in test_prompts:
        print(f"\nOriginal: {prompt}")
        result = baseline.refine(prompt)
        if "error" not in result:
            print(f"Refined:  {result['refined_prompt']}")
            print(f"Latency:  {result['refinement_latency_ms']:.1f}ms")
            print(f"Tokens (in/out): {result['refinement_input_tokens']}/{result['refinement_output_tokens']}")
        else:
            print(f"ERROR: {result['error']}")

