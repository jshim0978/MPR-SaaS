"""
SelfCheckGPT - Local Llama Version

Hallucination detection via self-consistency using local Llama models.
"""

import os
import time
import sys
sys.path.insert(0, '/home')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base import BaseHallucinationDetector, RefinementResult
from mpr.common.vllm_client import chat


class SelfCheckGPT_Local(BaseHallucinationDetector):
    """
    SelfCheckGPT using local Llama models via vLLM
    """
    
    def __init__(self, model_size: str = "3b", n_samples: int = 3):
        self.model_size = model_size.lower()
        if self.model_size == "3b":
            model_name = "Llama-3.2-3B"
            os.environ["MODEL_NAME"] = "meta-llama/Llama-3.2-3B-Instruct"
        elif self.model_size == "8b":
            model_name = "Llama-3.1-8B"
            os.environ["MODEL_NAME"] = "meta-llama/Llama-3.1-8B-Instruct"
        else:
            raise ValueError(f"Invalid model_size: {model_size}")
        
        super().__init__(name=f"SelfCheckGPT_Local_{model_name}")
        self.n_samples = n_samples
        self.model_name = model_name
    
    async def detect_hallucination(self, prompt: str) -> float:
        """Detect hallucination by checking self-consistency"""
        try:
            responses = []
            for _ in range(self.n_samples):
                response = await chat(
                    [{"role": "user", "content": prompt}],
                    temperature=1.0,  # High temp for diversity
                    max_tokens=200
                )
                responses.append(response["text"])
            
            # Simple consistency check: compare response lengths
            avg_length = sum(len(r.split()) for r in responses) / len(responses)
            length_variance = sum((len(r.split()) - avg_length) ** 2 for r in responses) / len(responses)
            
            # Normalize to 0-1 range
            hallucination_score = min(1.0, length_variance / (avg_length + 1))
            
            return hallucination_score
        
        except Exception:
            return 0.5  # Moderate risk on error
    
    def get_cost_per_token(self):
        if self.model_size == "8b":
            return {"input": 0.10 / 1_000_000, "output": 0.20 / 1_000_000}
        else:
            return {"input": 0.05 / 1_000_000, "output": 0.10 / 1_000_000}


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("="*80)
        print("SelfCheckGPT Local Test")
        print("="*80)
        
        for model_size in ["3b", "8b"]:
            print(f"\n--- Llama-{model_size.upper()} ---")
            detector = SelfCheckGPT_Local(model_size=model_size, n_samples=2)
            
            prompt = "What is the capital of France?"
            result = await detector.refine(prompt)
            
            if not result.error:
                score = result.metadata.get('hallucination_score', 0)
                print(f"Hallucination Score: {score:.3f}")
                print(f"Latency: {result.latency_ms:.1f}ms")
    
    asyncio.run(main())

