"""
OPRO (Optimization by PROmpting) - Yang et al., 2023

Reference: "Large Language Models as Optimizers"
Paper: https://arxiv.org/abs/2309.03409

Budget-matched variant: 1-iteration only (vs multiple iterations in original)

Core idea: Use an LLM as optimizer to generate better prompts by:
1. Starting with initial prompt
2. LLM generates optimization instructions
3. Apply instructions to improve prompt
4. Single iteration for budget matching
"""

import os
import time
from typing import Dict
import sys
sys.path.append('/home/comparison/frameworks')
from base import BasePromptOptimizer, RefinementResult

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OPRO_1iter(BasePromptOptimizer):
    """
    OPRO with 1 iteration for budget-matched comparison
    
    Original OPRO uses multiple iterations; we limit to 1 for fair comparison.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(name="OPRO (1-iter)", model=model, max_iterations=1)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package required for OPRO")
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Meta-prompt for optimization (simplified from paper)
        self.meta_prompt = """You are a prompt optimization system. Your task is to improve the given prompt to make it clearer, more specific, and less likely to produce hallucinated or incorrect outputs.

Given prompt: {prompt}

Analyze this prompt and generate an improved version that:
1. Fixes any grammatical errors or typos
2. Adds necessary context or constraints
3. Makes vague requests more specific
4. Preserves the original intent
5. Minimizes potential for hallucination

Output ONLY the improved prompt, with no explanations or additional text."""
    
    def refine(self, prompt: str) -> RefinementResult:
        """Single-iteration OPRO refinement"""
        t0 = time.perf_counter()
        
        try:
            # Single optimization step
            meta_instruction = self.meta_prompt.format(prompt=prompt)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a prompt optimization expert."},
                    {"role": "user", "content": meta_instruction}
                ],
                temperature=0.7,  # Some creativity for optimization
                max_tokens=500
            )
            
            refined_prompt = response.choices[0].message.content.strip()
            
            # Extract token usage
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
                    "iterations": 1,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "temperature": 0.7
                }
            )
        
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=prompt,  # Fallback to original
                latency_ms=latency_ms,
                tokens_used=len(prompt.split()) * 2,
                metadata={},
                error=str(e)
            )


if __name__ == "__main__":
    print("="*80)
    print("OPRO (1-iteration) Test")
    print("="*80)
    
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI not available. Install with: pip install openai")
        exit(1)
    
    try:
        opro = OPRO_1iter()
        
        test_prompts = [
            "what is the captial of frane?",
            "tell me about quantom physics",
            "how does photosythesis work"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n{i}. Original: {prompt}")
            result = opro.refine(prompt)
            
            if result.error:
                print(f"   ERROR: {result.error}")
            else:
                print(f"   Refined: {result.refined_prompt}")
                print(f"   Latency: {result.latency_ms:.1f}ms")
                print(f"   Tokens: {result.tokens_used}")
                print(f"   Cost: ${opro.calculate_cost(result.tokens_used):.6f}")
    
    except ValueError as e:
        print(f"\n❌ {e}")
        print("Set OPENAI_API_KEY environment variable to test")

