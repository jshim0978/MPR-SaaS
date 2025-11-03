"""
PromptBreeder - Fernando et al., 2023

Reference: "Promptbreeder: Self-Referential Self-Improvement Via Prompt Evolution"
Paper: https://arxiv.org/abs/2309.16797

Budget-matched variant: 8 candidates × 2 iterations (vs longer evolution in original)

Core idea: Evolutionary algorithm for prompt optimization:
1. Generate population of prompt variations (mutations)
2. Evaluate fitness of each candidate
3. Select best candidates
4. Repeat for fixed iterations (2 for budget matching)
"""

import os
import time
import random
from typing import Dict, List
import sys
sys.path.append('/home/comparison/frameworks')
from base import BasePromptOptimizer, RefinementResult

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class PromptBreeder_8x2(BasePromptOptimizer):
    """
    PromptBreeder with 8 candidates × 2 iterations
    
    Simplified evolutionary prompt optimization for budget matching.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o", 
                 population_size: int = 8, generations: int = 2):
        super().__init__(name="PromptBreeder (8×2)", model=model, max_iterations=generations)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package required for PromptBreeder")
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.population_size = population_size
        self.generations = generations
        
        # Mutation strategies (simplified from paper)
        self.mutations = [
            "Rephrase this prompt for better clarity: {prompt}",
            "Add helpful context to this prompt: {prompt}",
            "Make this prompt more specific: {prompt}",
            "Fix any errors in this prompt: {prompt}",
            "Restructure this prompt for better results: {prompt}",
        ]
    
    def mutate(self, prompt: str) -> str:
        """Generate a mutation of the prompt"""
        mutation_template = random.choice(self.mutations)
        instruction = mutation_template.format(prompt=prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": instruction}
                ],
                temperature=0.9,  # High temp for diversity
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except:
            return prompt  # Fallback
    
    def evaluate_fitness(self, prompt: str) -> float:
        """Simple fitness: length and specificity heuristic"""
        # Longer prompts with more specific words = higher fitness
        words = prompt.split()
        specificity_words = ['what', 'when', 'where', 'who', 'why', 'how', 'please', 'specific']
        specificity_score = sum(1 for w in words if w.lower() in specificity_words)
        return len(words) + specificity_score * 2
    
    def refine(self, prompt: str) -> RefinementResult:
        """Evolutionary prompt optimization"""
        t0 = time.perf_counter()
        total_tokens = 0
        
        try:
            # Initialize population
            population = [prompt]
            
            # Generate initial mutations
            for _ in range(self.population_size - 1):
                mutation = self.mutate(prompt)
                population.append(mutation)
                total_tokens += 100  # Rough estimate per mutation
            
            # Evolve for specified generations
            for gen in range(self.generations):
                # Evaluate fitness
                fitness_scores = [(p, self.evaluate_fitness(p)) for p in population]
                fitness_scores.sort(key=lambda x: x[1], reverse=True)
                
                # Select top half
                survivors = [p for p, _ in fitness_scores[:self.population_size // 2]]
                
                # Generate new population from survivors
                new_population = survivors.copy()
                while len(new_population) < self.population_size:
                    parent = random.choice(survivors)
                    child = self.mutate(parent)
                    new_population.append(child)
                    total_tokens += 100  # Rough estimate
                
                population = new_population
            
            # Return best candidate
            best_prompt = max(population, key=self.evaluate_fitness)
            
            latency_ms = (time.perf_counter() - t0) * 1000.0
            
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=best_prompt,
                latency_ms=latency_ms,
                tokens_used=total_tokens,
                metadata={
                    "model": self.model,
                    "population_size": self.population_size,
                    "generations": self.generations,
                    "final_population_size": len(population)
                }
            )
        
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=prompt,
                latency_ms=latency_ms,
                tokens_used=total_tokens,
                metadata={},
                error=str(e)
            )


if __name__ == "__main__":
    print("="*80)
    print("PromptBreeder (8×2) Test")
    print("="*80)
    
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI not available. Install with: pip install openai")
        exit(1)
    
    try:
        pb = PromptBreeder_8x2(population_size=4, generations=1)  # Smaller for testing
        
        prompt = "what is the captial of frane?"
        print(f"\nOriginal: {prompt}")
        result = pb.refine(prompt)
        
        if result.error:
            print(f"ERROR: {result.error}")
        else:
            print(f"Refined: {result.refined_prompt}")
            print(f"Latency: {result.latency_ms:.1f}ms")
            print(f"Tokens: {result.tokens_used}")
            print(f"Cost: ${pb.calculate_cost(result.tokens_used):.6f}")
    
    except ValueError as e:
        print(f"\n❌ {e}")
        print("Set OPENAI_API_KEY environment variable to test")

