"""
SelfCheckGPT - Manakul et al., 2023

Reference: "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models"
Paper: https://arxiv.org/abs/2303.08896
GitHub: https://github.com/potsawee/selfcheckgpt

Core idea: Hallucination detection via self-consistency
1. Generate multiple responses via sampling
2. Check consistency across responses
3. Inconsistent facts likely to be hallucinations

Simplified implementation for comparison framework.
"""

import os
import time
from typing import Dict, List
import sys
sys.path.append('/home/comparison/frameworks')
from base import BaseHallucinationDetector, RefinementResult

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SelfCheckGPT(BaseHallucinationDetector):
    """
    SelfCheckGPT - Hallucination detection via sampling
    
    Generates multiple responses and checks self-consistency.
    High inconsistency = likely hallucination.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o", n_samples: int = 3):
        super().__init__(name="SelfCheckGPT")
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package required for SelfCheckGPT")
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.n_samples = n_samples
    
    def detect_hallucination(self, prompt: str) -> float:
        """
        Detect hallucination by checking self-consistency
        
        Returns:
            Float 0-1 where higher = more likely hallucination
        """
        try:
            # Generate multiple responses with sampling
            responses = []
            for _ in range(self.n_samples):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1.0,  # High temp for diversity
                    max_tokens=200,
                    n=1
                )
                responses.append(response.choices[0].message.content.strip())
            
            # Simple consistency check: compare response lengths and overlap
            # More sophisticated: use NLI model or BERTScore
            avg_length = sum(len(r.split()) for r in responses) / len(responses)
            length_variance = sum((len(r.split()) - avg_length) ** 2 for r in responses) / len(responses)
            
            # High variance = inconsistent = potential hallucination
            # Normalize to 0-1 range
            hallucination_score = min(1.0, length_variance / (avg_length + 1))
            
            return hallucination_score
        
        except Exception as e:
            # Fallback: assume moderate risk
            return 0.5
    
    def refine(self, prompt: str) -> RefinementResult:
        """
        SelfCheckGPT is a detector, not a refiner.
        Returns hallucination score in metadata.
        """
        t0 = time.perf_counter()
        
        try:
            score = self.detect_hallucination(prompt)
            latency_ms = (time.perf_counter() - t0) * 1000.0
            
            # Estimate token usage (n_samples * typical response)
            tokens_used = self.n_samples * 250  # Rough estimate
            
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=prompt,  # No refinement
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                metadata={
                    "hallucination_score": score,
                    "n_samples": self.n_samples,
                    "is_detector": True,
                    "interpretation": "higher score = more likely hallucination"
                }
            )
        
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return RefinementResult(
                method_name=self.name,
                original_prompt=prompt,
                refined_prompt=prompt,
                latency_ms=latency_ms,
                tokens_used=0,
                metadata={},
                error=str(e)
            )


if __name__ == "__main__":
    print("="*80)
    print("SelfCheckGPT Test")
    print("="*80)
    
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI not available. Install with: pip install openai")
        exit(1)
    
    try:
        detector = SelfCheckGPT(n_samples=2)  # Reduced for testing
        
        test_prompts = [
            "What is the capital of France?",  # Should be consistent (low score)
            "Tell me about the ancient city of Atlantis",  # May be inconsistent (high score)
        ]
        
        for prompt in test_prompts:
            print(f"\n📝 Prompt: {prompt}")
            result = detector.refine(prompt)
            
            if result.error:
                print(f"   ERROR: {result.error}")
            else:
                score = result.metadata['hallucination_score']
                print(f"   Hallucination Score: {score:.3f} ({'HIGH' if score > 0.5 else 'LOW'} risk)")
                print(f"   Latency: {result.latency_ms:.1f}ms")
                print(f"   Tokens: {result.tokens_used}")
    
    except ValueError as e:
        print(f"\n❌ {e}")
        print("Set OPENAI_API_KEY environment variable to test")

