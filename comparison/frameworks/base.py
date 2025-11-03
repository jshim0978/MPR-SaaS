"""
Standardized Method Interface for Comparison Frameworks

All SOTA methods implement this interface for uniform evaluation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass
import time


@dataclass
class RefinementResult:
    """Standardized result from any refinement method"""
    method_name: str
    original_prompt: str
    refined_prompt: str
    latency_ms: float
    tokens_used: int
    metadata: Dict
    error: Optional[str] = None


class StandardizedMethod(ABC):
    """Base class for all comparison methods"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def refine(self, prompt: str) -> RefinementResult:
        """
        Refine a prompt using this method
        
        Args:
            prompt: Original user prompt
            
        Returns:
            RefinementResult with refined prompt and metrics
        """
        pass
    
    @abstractmethod
    def get_cost_per_token(self) -> Dict[str, float]:
        """
        Get cost per token for this method
        
        Returns:
            Dict with 'input' and 'output' cost per token (USD)
        """
        pass
    
    def calculate_cost(self, tokens_used: int) -> float:
        """Calculate total cost for token usage"""
        costs = self.get_cost_per_token()
        # Simplified: assume 50/50 split between input/output
        return tokens_used * (costs['input'] + costs['output']) / 2
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"


class BasePromptOptimizer(StandardizedMethod):
    """Base class for global prompt optimizers (OPRO, PromptBreeder, etc.)"""
    
    def __init__(self, name: str, model: str = "gpt-4o", max_iterations: int = 1):
        super().__init__(name)
        self.model = model
        self.max_iterations = max_iterations
    
    def get_cost_per_token(self) -> Dict[str, float]:
        """Cost for GPT-4o (most optimizers use commercial LLMs)"""
        if "gpt-4o" in self.model.lower():
            return {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000}
        elif "gpt-3.5" in self.model.lower():
            return {"input": 0.50 / 1_000_000, "output": 1.50 / 1_000_000}
        else:
            return {"input": 1.00 / 1_000_000, "output": 3.00 / 1_000_000}


class BaseHallucinationDetector(StandardizedMethod):
    """Base class for hallucination detection methods (SelfCheckGPT, CoVe)"""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    def refine(self, prompt: str) -> RefinementResult:
        """
        Detection methods don't refine, they verify.
        For comparison, we return hallucination score in metadata.
        """
        t0 = time.perf_counter()
        score = self.detect_hallucination(prompt)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        
        return RefinementResult(
            method_name=self.name,
            original_prompt=prompt,
            refined_prompt=prompt,  # No refinement
            latency_ms=latency_ms,
            tokens_used=len(prompt.split()) * 2,  # Rough estimate
            metadata={"hallucination_score": score, "is_detector": True}
        )
    
    @abstractmethod
    def detect_hallucination(self, prompt: str) -> float:
        """
        Detect hallucination probability
        
        Returns:
            Float between 0-1, where 1 = high hallucination risk
        """
        pass
    
    def get_cost_per_token(self) -> Dict[str, float]:
        """Most detectors use sampling, similar to GPT-4o cost"""
        return {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000}


if __name__ == "__main__":
    # Test the interface
    class DummyMethod(StandardizedMethod):
        def refine(self, prompt: str) -> RefinementResult:
            return RefinementResult(
                method_name="dummy",
                original_prompt=prompt,
                refined_prompt=prompt.upper(),
                latency_ms=1.0,
                tokens_used=10,
                metadata={}
            )
        
        def get_cost_per_token(self) -> Dict[str, float]:
            return {"input": 0.001, "output": 0.003}
    
    method = DummyMethod("test")
    result = method.refine("hello world")
    print(f"Method: {method}")
    print(f"Result: {result}")
    print(f"Cost: ${method.calculate_cost(result.tokens_used):.6f}")

