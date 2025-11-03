"""
PromptAgent - Wang et al., 2024b

Reference: Strategic prompt planning approach
Cited in manuscript as comparison baseline

Core idea: Multi-agent strategic planning for prompt optimization
1. Planner agent: Analyze prompt and create optimization strategy
2. Executor agent: Apply improvements based on strategy
3. Evaluator agent: Score the result
4. Single-pass variant for budget matching

Simplified implementation based on strategic planning methodology.
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


class PromptAgent_1pass(BasePromptOptimizer):
    """
    PromptAgent - Strategic prompt planning (1-pass variant)
    
    Multi-agent approach: Plan→Execute in single pass
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(name="PromptAgent (1-pass)", model=model, max_iterations=1)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package required for PromptAgent")
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Strategic planning prompt
        self.planning_prompt = """You are a strategic prompt optimization agent. Analyze this prompt and create an improvement plan:

Prompt: {prompt}

Strategic Analysis:
1. Identify issues (typos, ambiguity, missing context, vague requests)
2. Plan improvements (what to fix, what to add, what to clarify)
3. Execute improvements

Output ONLY the improved prompt, incorporating all planned improvements."""
    
    def refine(self, prompt: str) -> RefinementResult:
        """Single-pass strategic planning"""
        t0 = time.perf_counter()
        
        try:
            # Single strategic planning call
            planning_instruction = self.planning_prompt.format(prompt=prompt)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strategic prompt optimization expert."},
                    {"role": "user", "content": planning_instruction}
                ],
                temperature=0.5,  # Balanced for planning
                max_tokens=400
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
                    "approach": "strategic_planning",
                    "agents": "planner+executor (fused)",
                    "passes": 1,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "temperature": 0.5
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
    print("PromptAgent (1-pass) Test")
    print("="*80)
    
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI not available. Install with: pip install openai")
        exit(1)
    
    try:
        agent = PromptAgent_1pass()
        
        test_prompts = [
            "what is the captial of frane?",
            "tell me about quantom physics",
            "how does photosythesis work"
        ]
        
        for prompt in test_prompts:
            print(f"\nOriginal: {prompt}")
            result = agent.refine(prompt)
            
            if result.error:
                print(f"ERROR: {result.error}")
            else:
                print(f"Refined: {result.refined_prompt}")
                print(f"Latency: {result.latency_ms:.1f}ms")
                print(f"Tokens: {result.tokens_used}")
                print(f"Cost: ${agent.calculate_cost(result.tokens_used):.6f}")
    
    except ValueError as e:
        print(f"\n❌ {e}")
        print("Set OPENAI_API_KEY environment variable to test")

