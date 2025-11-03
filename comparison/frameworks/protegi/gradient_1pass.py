"""
ProTeGi - Ramnath et al., 2023

Reference: Textual gradients for prompt optimization
Cited in manuscript for fallback mechanism

Core idea: Gradient-based prompt search
1. Start with initial prompt
2. Compute "textual gradient" (improvement direction)
3. Apply gradient to optimize prompt
4. Single-pass variant for budget matching

Note: Original ProTeGi uses iterative gradient descent.
We implement 1-pass for budget matching with MPR-SaaS.
"""

import os
import time
from typing import Dict
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base import BasePromptOptimizer, RefinementResult

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ProTeGi_1pass(BasePromptOptimizer):
    """
    ProTeGi - Textual Gradients (1-pass variant)
    
    Gradient-based optimization for prompts.
    Single gradient step for budget matching.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(name="ProTeGi (1-pass)", model=model, max_iterations=1)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package required for ProTeGi")
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Gradient computation prompt
        self.gradient_prompt = """You are a textual gradient optimizer. Given a prompt, compute the improvement direction and apply a single optimization step.

Current prompt: {prompt}

Task:
1. Identify what makes this prompt suboptimal (gradient direction)
2. Apply a single improvement step along that gradient
3. Output the optimized prompt

Focus on: clarity, specificity, grammar, completeness.
Output ONLY the improved prompt."""
    
    def refine(self, prompt: str) -> RefinementResult:
        """Single gradient step optimization"""
        t0 = time.perf_counter()
        
        try:
            # Single gradient step
            gradient_instruction = self.gradient_prompt.format(prompt=prompt)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a gradient-based optimization expert."},
                    {"role": "user", "content": gradient_instruction}
                ],
                temperature=0.4,  # Low temp for focused optimization
                max_tokens=350
            )
            
            refined_prompt = response.choices[0].message.content.strip()
            
            # Token usage
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            
            latency_ms = (time.perf_counter() - t0) * 1000.0
            
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=refined_prompt,
                latency_ms=latency_ms,
                tokens_used=total_tokens,
                metadata={
                    "model": self.model,
                    "approach": "textual_gradients",
                    "gradient_steps": 1,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "temperature": 0.4
                }
            )
        
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=prompt,
                latency_ms=latency_ms,
                tokens_used=len(prompt.split()) * 2,
                metadata={},
                error=str(e)
            )


if __name__ == "__main__":
    print("="*80)
    print("ProTeGi (1-pass) Test")
    print("="*80)
    
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI not available. Install with: pip install openai")
        exit(1)
    
    try:
        protegi = ProTeGi_1pass()
        
        test_prompts = [
            "what is the captial of frane?",
            "tell me about quantom physics"
        ]
        
        for prompt in test_prompts:
            print(f"\nOriginal: {prompt}")
            result = protegi.refine(prompt)
            
            if result.error:
                print(f"ERROR: {result.error}")
            else:
                print(f"Refined: {result.refined_prompt}")
                print(f"Latency: {result.latency_ms:.1f}ms")
                print(f"Tokens: {result.tokens_used}")
                print(f"Cost: ${protegi.calculate_cost(result.tokens_used):.6f}")
    
    except ValueError as e:
        print(f"\n❌ {e}")
        print("Set OPENAI_API_KEY environment variable to test")

