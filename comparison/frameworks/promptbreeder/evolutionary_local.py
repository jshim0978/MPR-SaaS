"""
PromptBreeder (Simplified) - Local Llama Version

Evolutionary optimization using local Llama models.
Simplified to 4×1 (4 candidates, 1 generation) for faster comparison.
"""

import os
import time
import random
import sys
sys.path.insert(0, '/home')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base import BasePromptOptimizer, RefinementResult
from mpr.common.vllm_client import chat


class PromptBreeder_Local(BasePromptOptimizer):
    """
    PromptBreeder using local Llama models via vLLM
    
    Simplified: 4 candidates × 1 generation (vs 8×2 for OpenAI version)
    """
    
    def __init__(self, model_size: str = "3b", num_candidates: int = 4):
        self.model_size = model_size.lower()
        if self.model_size == "3b":
            model_name = "Llama-3.2-3B"
            os.environ["MODEL_NAME"] = "meta-llama/Llama-3.2-3B-Instruct"
        elif self.model_size == "8b":
            model_name = "Llama-3.1-8B"
            os.environ["MODEL_NAME"] = "meta-llama/Llama-3.1-8B-Instruct"
        else:
            raise ValueError(f"Invalid model_size: {model_size}")
        
        super().__init__(name=f"PromptBreeder_Local_{model_name}", model=model_name, max_iterations=1)
        self.num_candidates = num_candidates
        
        self.mutation_prompt = """Given an original prompt, generate a slightly modified version.
The goal is to explore variations that might lead to better responses, focusing on clarity and completeness.
Keep the core intent.

Original Prompt: {original_prompt}
Current Prompt: {current_prompt}

Output ONLY the mutated prompt:"""
    
    async def _evaluate_prompt(self, original_prompt: str, candidate_prompt: str) -> int:
        """Simple evaluation: score based on length and clarity (heuristic)"""
        # In real scenario, you'd call target LLM and score response quality
        # For now, use simple heuristics
        score = len(candidate_prompt.split())  # Longer = more detailed (simplified)
        if "?" in candidate_prompt:
            score += 5
        if any(word in candidate_prompt.lower() for word in ["please", "specific", "detailed", "explain"]):
            score += 3
        return score
    
    async def refine(self, prompt: str) -> RefinementResult:
        """Simplified evolutionary optimization"""
        t0 = time.perf_counter()
        total_tokens = 0
        
        current_best_prompt = prompt
        current_best_score = await self._evaluate_prompt(prompt, prompt)
        
        try:
            # Generate candidates
            candidates = []
            for i in range(self.num_candidates):
                mutation_instruction = self.mutation_prompt.format(
                    original_prompt=prompt,
                    current_prompt=current_best_prompt
                )
                
                response = await chat([{"role": "user", "content": mutation_instruction}], temperature=0.8, max_tokens=256)
                mutated_prompt = response["text"]
                total_tokens += len(mutation_instruction.split()) * 1.3 + len(mutated_prompt.split()) * 1.3
                
                candidates.append(mutated_prompt)
            
            # Evaluate candidates
            candidate_scores = []
            for candidate in candidates:
                score = await self._evaluate_prompt(prompt, candidate)
                candidate_scores.append((candidate, score))
            
            # Select best
            if candidate_scores:
                best_candidate, best_score = max(candidate_scores, key=lambda item: item[1])
                if best_score > current_best_score:
                    current_best_prompt = best_candidate
                    current_best_score = best_score
            
            latency_ms = (time.perf_counter() - t0) * 1000.0
            
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=current_best_prompt,
                latency_ms=latency_ms,
                tokens_used=int(total_tokens),
                metadata={
                    "model": self.model,
                    "model_size": self.model_size,
                    "num_candidates": self.num_candidates,
                    "num_generations": 1,
                    "final_score": current_best_score
                }
            )
        
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=prompt,
                latency_ms=latency_ms,
                tokens_used=int(total_tokens),
                metadata={},
                error=f"vLLM Error: {e}"
            )
    
    def get_cost_per_token(self):
        if self.model_size == "8b":
            return {"input": 0.10 / 1_000_000, "output": 0.20 / 1_000_000}
        else:
            return {"input": 0.05 / 1_000_000, "output": 0.10 / 1_000_000}


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("="*80)
        print("PromptBreeder Local Test (Simplified 4×1)")
        print("="*80)
        
        for model_size in ["3b", "8b"]:
            print(f"\n--- Llama-{model_size.upper()} ---")
            pb = PromptBreeder_Local(model_size=model_size, num_candidates=2)  # Reduced for test
            
            prompt = "what is the captial of frane?"
            result = await pb.refine(prompt)
            
            if not result.error:
                print(f"Refined: {result.refined_prompt}")
                print(f"Latency: {result.latency_ms:.1f}ms")
                print(f"Score: {result.metadata.get('final_score', 0)}")
    
    asyncio.run(main())

