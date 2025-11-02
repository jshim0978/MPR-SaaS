"""
Baseline 4: GPT-4 Refinement

Use GPT-4o to refine prompts before sending to target LLM.
High cost, high latency, but potentially high quality.
"""

import time
import os
from typing import Dict
import tiktoken

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Install with: pip install openai")


class GPT4RefineBaseline:
    def __init__(self, api_key: str = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available")
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.encoder = tiktoken.get_encoding("cl100k_base")
        
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
        Use GPT-4o to refine the prompt
        
        Returns:
            refined_prompt: GPT-4 improved version
            latency_ms: API call latency
            tokens: Token counts for cost calculation
        """
        t0 = time.perf_counter()
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            refined_prompt = response.choices[0].message.content.strip()
            
            # Token usage from API
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            latency_ms = (time.perf_counter() - t0) * 1000.0
            
            return {
                "method": "gpt4_refine",
                "original_prompt": prompt,
                "refined_prompt": refined_prompt,
                "refinement_latency_ms": latency_ms,
                "prompt_tokens": self.count_tokens(refined_prompt),
                "refinement_tokens_added": self.count_tokens(refined_prompt) - self.count_tokens(prompt),
                "refinement_input_tokens": input_tokens,
                "refinement_output_tokens": output_tokens,
                "metadata": {
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "description": "GPT-4o-based prompt refinement"
                }
            }
        
        except Exception as e:
            # Fallback to passthrough on error
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return {
                "method": "gpt4_refine",
                "original_prompt": prompt,
                "refined_prompt": prompt,  # Fallback
                "refinement_latency_ms": latency_ms,
                "prompt_tokens": self.count_tokens(prompt),
                "refinement_tokens_added": 0,
                "error": str(e),
                "metadata": {
                    "description": "GPT-4o refinement failed, using original prompt"
                }
            }
    
    def __str__(self):
        return "GPT-4o Refinement"


if __name__ == "__main__":
    if not OPENAI_AVAILABLE:
        print("OpenAI not available. Install with: pip install openai")
        exit(1)
    
    baseline = GPT4RefineBaseline()
    
    test_prompts = [
        "what is the captial of frane?",
        "tell me about quantom physics",
        "how does photosythesis work",
    ]
    
    print("="*80)
    print("GPT-4 REFINEMENT BASELINE TEST")
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

