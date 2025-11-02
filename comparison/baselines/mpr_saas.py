"""
Baseline 6: MPR-SaaS (Our System)

Call the MPR-SaaS orchestrator running on jw1.
3-worker parallel refinement (Cleaner || Describer || Paraphraser)
"""

import time
import httpx
import tiktoken
from typing import Dict

class MPRSaaSBaseline:
    def __init__(self, orchestrator_url: str = "http://129.254.202.251:8000"):
        self.orchestrator_url = orchestrator_url
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))
    
    def refine(self, prompt: str, timeout: float = 10.0) -> Dict:
        """
        Call MPR-SaaS orchestrator
        
        Returns:
            refined_prompt: Final merged prompt from orchestrator
            latency_ms: End-to-end refinement time
            worker_stats: Individual worker metrics
        """
        t0 = time.perf_counter()
        
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    f"{self.orchestrator_url}/refine",
                    json={"prompt": prompt}
                )
                response.raise_for_status()
                data = response.json()
            
            refined_prompt = data.get("final_prompt", prompt)
            
            latency_ms = (time.perf_counter() - t0) * 1000.0
            
            # Extract worker metrics
            latency_breakdown = data.get("latency_ms", {})
            
            return {
                "method": "mpr_saas",
                "original_prompt": prompt,
                "refined_prompt": refined_prompt,
                "refinement_latency_ms": latency_ms,
                "prompt_tokens": self.count_tokens(refined_prompt),
                "refinement_tokens_added": self.count_tokens(refined_prompt) - self.count_tokens(prompt),
                "metadata": {
                    "orchestrator_url": self.orchestrator_url,
                    "cleaner_latency_ms": latency_breakdown.get("cleaner", 0),
                    "descr_latency_ms": latency_breakdown.get("descr", 0),
                    "para_latency_ms": latency_breakdown.get("para", 0),
                    "total_latency_ms": latency_breakdown.get("total", 0),
                    "cleaned": data.get("cleaned", {}),
                    "described": data.get("described", {}),
                    "paraphrased": data.get("paraphrased", {}),
                    "description": "MPR-SaaS 3-worker parallel refinement"
                }
            }
        
        except Exception as e:
            # Fallback to passthrough on error
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return {
                "method": "mpr_saas",
                "original_prompt": prompt,
                "refined_prompt": prompt,  # Fallback
                "refinement_latency_ms": latency_ms,
                "prompt_tokens": self.count_tokens(prompt),
                "refinement_tokens_added": 0,
                "error": str(e),
                "metadata": {
                    "description": "MPR-SaaS call failed, using original prompt"
                }
            }
    
    def __str__(self):
        return "MPR-SaaS (Our System)"


if __name__ == "__main__":
    baseline = MPRSaaSBaseline()
    
    test_prompts = [
        "what is the captial of frane?",
        "tell me about quantom physics",
        "how does photosythesis work",
    ]
    
    print("="*80)
    print("MPR-SAAS BASELINE TEST")
    print("="*80)
    print(f"Orchestrator: {baseline.orchestrator_url}")
    print()
    
    for prompt in test_prompts:
        print(f"\nOriginal: {prompt}")
        result = baseline.refine(prompt)
        if "error" not in result:
            print(f"Refined:  {result['refined_prompt']}")
            print(f"Latency:  {result['refinement_latency_ms']:.1f}ms")
            print(f"  - Cleaner:  {result['metadata']['cleaner_latency_ms']:.1f}ms")
            print(f"  - Describer: {result['metadata']['descr_latency_ms']:.1f}ms")
            print(f"  - Paraphraser: {result['metadata']['para_latency_ms']:.1f}ms")
            print(f"Tokens added: {result['refinement_tokens_added']}")
        else:
            print(f"ERROR: {result['error']}")

