#!/usr/bin/env python3
"""
Unified Evaluation Harness for PRaaS Multi-Benchmark Evaluation.

Supports:
- BBH (Big-Bench Hard): Reasoning
- TruthfulQA: Truthfulness
- GSM8k: Math
- CommonsenseQA: Commonsense reasoning
- StrategyQA: Logic
- HaluEval: Hallucination detection

Collects 11 metrics:
1. Raw answers
2. Accuracy (%)
3. Latency (ms)
4. Output tokens
5. Cost ($)
6. Worker utilization & routing
7. Edit conservatism (semantic drift)
8. Portability
9. Format robustness
10. Routing accuracy
11. Fallback impact
"""

import json
import time
import asyncio
import httpx
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from tqdm.asyncio import tqdm as async_tqdm
import re
import wandb
import os
from difflib import SequenceMatcher

# Worker endpoints
ORCHESTRATOR_URL = "http://localhost:8000/infer"

DEFAULT_ORCHESTRATOR_PAYLOAD = {
    "merge_strategy": "adaptive",
}

# Target LLM endpoints (OpenAI-compatible vLLM servers)
TARGET_ENDPOINTS = [
    {
        "name": "jw2",
        "url": "http://129.254.202.252:8001/v1/chat/completions"
    },
    {
        "name": "jw3",
        "url": "http://129.254.202.253:8001/v1/chat/completions"
    },
    {
        "name": "kcloud",
        "url": "http://129.254.202.129:8004/generate"  # Worker exposes OpenAI-compatible /generate
    },
]

TARGET_LLM_REQUEST = {
    "model": "meta-llama/Llama-3.2-3B-Instruct",
    "temperature": 0.2,
    "top_p": 0.95,
    "max_tokens": 256,
    "seed": 2025,
}

@dataclass
class EvaluationSample:
    """Single evaluation sample."""
    benchmark: str
    question: str
    answer: str
    metadata: Dict[str, Any]
    
    # Original fields
    original_prompt: str = ""
    
    # Refinement outputs
    refined_prompt: str = ""
    arbiter_decision: Dict = None
    worker_outputs: Dict = None
    merge_result: Dict = None
    
    # Q&A outputs
    original_output: str = ""
    refined_output: str = ""
    
    # Metrics
    accuracy_original: float = 0.0
    accuracy_refined: float = 0.0
    latency_refinement_ms: float = 0.0
    latency_qa_original_ms: float = 0.0
    latency_qa_refined_ms: float = 0.0
    tokens_refinement: int = 0
    tokens_qa_original: int = 0
    tokens_qa_refined: int = 0
    cost_refinement: float = 0.0
    cost_qa_original: float = 0.0
    cost_qa_refined: float = 0.0
    semantic_drift: float = 0.0
    workers_used: List[str] = None
    routing_decision: str = ""
    refinement_latency_breakdown: Dict[str, float] = None
    refinement_token_details: Dict[str, Any] = None
    refinement_cost_details: Dict[str, Any] = None
    refinement_helped: Optional[str] = None
    hallucinated_answer: Optional[str] = None
    hallucination_original: Optional[bool] = None
    hallucination_refined: Optional[bool] = None
    
    def __post_init__(self):
        if self.workers_used is None:
            self.workers_used = []
        if self.arbiter_decision is None:
            self.arbiter_decision = {}
        if self.worker_outputs is None:
            self.worker_outputs = {}
        if self.merge_result is None:
            self.merge_result = {}
        if self.refinement_latency_breakdown is None:
            self.refinement_latency_breakdown = {}
        if self.refinement_token_details is None:
            self.refinement_token_details = {}
        if self.refinement_cost_details is None:
            self.refinement_cost_details = {}


class BenchmarkLoader:
    """Load benchmark datasets."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def load_benchmark(self, benchmark_name: str, max_samples: int = -1) -> List[EvaluationSample]:
        """Load a specific benchmark."""
        file_path = self.data_dir / f"{benchmark_name}.jsonl"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Benchmark file not found: {file_path}")
        
        samples = []
        with open(file_path) as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    metadata = dict(data.get("metadata", {}))
                    if "choices" in data:
                        metadata["choices"] = data["choices"]
                    
                    # Create evaluation sample
                    sample = EvaluationSample(
                        benchmark=data["benchmark"],
                        question=data["question"],
                        answer=self._canonical_answer(data),
                        metadata=metadata,
                        original_prompt=self._format_prompt(data),
                        hallucinated_answer=data.get("hallucinated_answer")
                    )
                    samples.append(sample)
                    
                    if max_samples > 0 and len(samples) >= max_samples:
                        break
        
        return samples
    
    @staticmethod
    def _canonical_answer(data: Dict[str, Any]) -> str:
        benchmark = data.get("benchmark", "")
        answer = (data.get("answer") or "").strip()
        
        if benchmark == "gsm8k":
            hash_matches = re.findall(r'####\s*([-+]?\d[\d,]*(?:\.\d+)?)', answer)
            if hash_matches:
                return hash_matches[-1].replace(',', '')
            numeric = re.findall(r'-?\d[\d,]*(?:\.\d+)?', answer)
            if numeric:
                return numeric[-1].replace(',', '')
            return answer
        
        if benchmark == "commonsenseqa":
            letter = answer.upper()
            choices = data.get("choices", [])
            if len(letter) == 1 and 'A' <= letter <= 'E':
                idx = ord(letter) - ord('A')
                if 0 <= idx < len(choices):
                    return choices[idx]
            return answer
        
        return answer
    
    def _format_prompt(self, data: Dict) -> str:
        """Format raw data into a prompt."""
        benchmark = data["benchmark"]
        question = data["question"]
        
        if benchmark == "bbh":
            return f"Question: {question}\nAnswer:"
        
        elif benchmark == "truthfulqa":
            return f"Question: {question}\nProvide a truthful and accurate answer:"
        
        elif benchmark == "gsm8k":
            return f"Solve this math problem step by step:\n{question}\nAnswer:"
        
        elif benchmark == "commonsenseqa":
            choices = data.get("choices", [])
            choices_text = "\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])
            return f"Question: {question}\n{choices_text}\nAnswer:"
        
        elif benchmark == "strategyqa":
            return f"Question: {question}\nAnswer (yes/no):"
        
        elif benchmark == "halueval":
            knowledge = data.get("knowledge", "")
            if knowledge:
                return f"Context: {knowledge}\nQuestion: {question}\nAnswer:"
            else:
                return f"Question: {question}\nAnswer:"
        
        else:
            return question


class AccuracyEvaluator:
    """Evaluate accuracy for different benchmarks."""
    
    @staticmethod
    def normalize_answer(answer: str, benchmark: Optional[str] = None) -> str:
        """Normalize answer for comparison."""
        answer = (answer or "").lower()
        # Collapse whitespace to mirror vendor normalize_text
        return ' '.join(answer.split())
    
    @staticmethod
    def extract_answer(output: str, benchmark: str) -> str:
        """Extract answer from model output."""
        if not output:
            return ""
        return output.strip()
    
    def evaluate(self, benchmark: str, predicted: str, ground_truth: str) -> float:
        """Evaluate accuracy for a single sample."""
        pred = self.normalize_answer(self.extract_answer(predicted, benchmark), benchmark)
        gt = self.normalize_answer(ground_truth, benchmark)
        
        if not pred or not gt:
            return 0.0
        
        # Vendor logic: answer must appear in prediction (or as suffix)
        if gt in pred or pred.endswith(gt):
            return 1.0
        
        return 0.0

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a, b).ratio()

    def detect_hallucination(
        self,
        predicted: str,
        ground_truth: str,
        hallucinated_answer: Optional[str]
    ) -> bool:
        """Return True if output matches hallucinated reference more than truth."""
        pred = self.normalize_answer(predicted)
        truth = self.normalize_answer(ground_truth)
        hallu = self.normalize_answer(hallucinated_answer or "")

        if not pred:
            return False
        if truth and self._similarity(pred, truth) >= 0.9:
            return False
        if hallu:
            sim_hallu = self._similarity(pred, hallu)
            sim_truth = self._similarity(pred, truth) if truth else 0.0
            if sim_hallu >= max(sim_truth, 0.5):
                return True
        return False


class PRaaSEvaluator:
    """Main evaluation harness for PRaaS."""
    
    def __init__(
        self,
        data_dir: Path,
        results_dir: Path,
        use_wandb: bool = True,
        orchestrator_url: str = ORCHESTRATOR_URL,
        orchestrator_payload: Optional[Dict[str, Any]] = None,
        target_endpoints: Optional[List[Dict[str, str]]] = None,
        target_llm_request: Optional[Dict[str, Any]] = None,
        wandb_project: Optional[str] = None,
        wandb_entity: Optional[str] = None,
        wandb_run_name: Optional[str] = None,
    ):
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.loader = BenchmarkLoader(data_dir)
        self.accuracy_evaluator = AccuracyEvaluator()
        self.use_wandb = use_wandb
        self._endpoint_index = 0
        self.orchestrator_url = orchestrator_url
        self.orchestrator_payload = {
            **DEFAULT_ORCHESTRATOR_PAYLOAD,
            **(orchestrator_payload or {})
        }
        self.target_endpoints = target_endpoints or list(TARGET_ENDPOINTS)
        self.target_llm_request = dict(TARGET_LLM_REQUEST)
        if target_llm_request:
            self.target_llm_request.update(target_llm_request)
        
        # Initialize wandb if enabled
        if self.use_wandb and not wandb.run:
            project_name = wandb_project or "mpr-saas-evaluation"
            run_name = wandb_run_name or f"eval_{results_dir.name}"
            wandb.init(
                project=project_name,
                name=run_name,
                entity=wandb_entity,
                config={
                    "model": self.target_llm_request.get("model", "llama-3.2-3b-instruct"),
                    "total_samples": 44971,
                    "benchmarks": ["bbh", "truthfulqa", "gsm8k", "commonsenseqa", "strategyqa", "halueval"]
                }
            )
    
    async def refine_prompt(self, prompt: str, run_id: str) -> Dict:
        """Call PRaaS orchestrator to refine prompt."""
        t0 = time.perf_counter()
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.orchestrator_url,
                    json={
                        "prompt": prompt,
                        "run_id": run_id,
                        **self.orchestrator_payload
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                latency_ms = (time.perf_counter() - t0) * 1000.0
                worker_outputs = {
                    "cleaner": data.get("cleaned"),
                    "describer": data.get("described"),
                    "paraphraser": data.get("paraphrased"),
                }
                worker_outputs = {k: v for k, v in worker_outputs.items() if v}
                latency_breakdown = data.get("latency_ms") or {}
                token_detail = data.get("tokens") or {}
                cost_detail = data.get("cost") or {}
                tokens_total = (
                    token_detail.get("input_tokens", 0) + token_detail.get("output_tokens", 0)
                )
                cost_total = cost_detail.get("total_cost_usd", 0.0)
                
                return {
                    "refined_prompt": data.get("final_prompt", prompt),
                    "arbiter_decision": data.get("arbiter_decision", {}),
                    "worker_outputs": worker_outputs,
                    "merge_result": data.get("merge_result", {}),
                    "latency_ms": latency_ms,
                    "latency_breakdown": latency_breakdown,
                    "tokens": tokens_total,
                    "tokens_detail": token_detail,
                    "cost": cost_total,
                    "cost_detail": cost_detail,
                }
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return {
                "refined_prompt": prompt,  # Fallback to original
                "arbiter_decision": {},
                "worker_outputs": {},
                "merge_result": {},
                "latency_ms": latency_ms,
                "tokens": 0,
                "tokens_detail": {},
                "latency_breakdown": {},
                "cost": 0.0,
                "cost_detail": {},
                "error": str(e)
            }
    
    def _next_endpoint(self) -> Dict[str, str]:
        """Round-robin over available target endpoints."""
        endpoint = self.target_endpoints[self._endpoint_index % len(self.target_endpoints)]
        self._endpoint_index = (self._endpoint_index + 1) % len(self.target_endpoints)
        return endpoint

    async def generate_answer(self, prompt: str) -> Dict:
        """Generate answer using target vLLM endpoints."""
        t0 = time.perf_counter()
        endpoint = self._next_endpoint()

        payload = {
            **self.target_llm_request,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(endpoint["url"], json=payload)
                response.raise_for_status()
                data = response.json()

            latency_ms = (time.perf_counter() - t0) * 1000.0
            choices = data.get("choices", [])
            message = ""
            if choices:
                first_choice = choices[0]
                message = first_choice.get("message", {}).get("content", "")

            usage = data.get("usage", {})
            tokens_in = usage.get("prompt_tokens", 0)
            tokens_out = usage.get("completion_tokens", 0)

            return {
                "output": message,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "latency_ms": latency_ms,
                "endpoint": endpoint["name"],
            }
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return {
                "output": f"ERROR: {e}",
                "tokens_in": 0,
                "tokens_out": 0,
                "latency_ms": latency_ms,
                "error": str(e),
                "endpoint": endpoint["name"],
            }
    
    def calculate_semantic_drift(self, original: str, refined: str) -> float:
        """Calculate semantic drift between prompts."""
        # Simple word overlap-based drift
        orig_words = set(original.lower().split())
        ref_words = set(refined.lower().split())
        
        if not orig_words:
            return 0.0
        
        overlap = len(orig_words & ref_words) / len(orig_words)
        drift = 1.0 - overlap
        
        return drift
    
    async def evaluate_sample(self, sample: EvaluationSample, run_id: str) -> EvaluationSample:
        """Evaluate a single sample."""
        # Step 1: Refine prompt
        refine_result = await self.refine_prompt(sample.original_prompt, run_id)
        sample.refined_prompt = refine_result["refined_prompt"]
        sample.arbiter_decision = refine_result["arbiter_decision"]
        sample.worker_outputs = refine_result["worker_outputs"]
        sample.merge_result = refine_result["merge_result"]
        sample.latency_refinement_ms = refine_result["latency_ms"]
        sample.tokens_refinement = refine_result["tokens"]
        sample.cost_refinement = refine_result["cost"]
        sample.refinement_latency_breakdown = refine_result.get("latency_breakdown", {})
        sample.refinement_token_details = refine_result.get("tokens_detail", {})
        sample.refinement_cost_details = refine_result.get("cost_detail", {})
        
        # Extract workers used
        if isinstance(sample.arbiter_decision, dict):
            sample.workers_used = sample.arbiter_decision.get("chosen_branches", [])
            sample.routing_decision = " + ".join(sample.workers_used)
        
        # Calculate semantic drift
        sample.semantic_drift = self.calculate_semantic_drift(
            sample.original_prompt,
            sample.refined_prompt
        )
        
        # Step 2: Generate answers
        original_qa = await self.generate_answer(sample.original_prompt)
        sample.original_output = original_qa["output"]
        sample.latency_qa_original_ms = original_qa["latency_ms"]
        sample.tokens_qa_original = original_qa["tokens_in"] + original_qa["tokens_out"]
        
        refined_qa = await self.generate_answer(sample.refined_prompt)
        sample.refined_output = refined_qa["output"]
        sample.latency_qa_refined_ms = refined_qa["latency_ms"]
        sample.tokens_qa_refined = refined_qa["tokens_in"] + refined_qa["tokens_out"]
        
        # Step 3: Evaluate accuracy
        sample.accuracy_original = self.accuracy_evaluator.evaluate(
            sample.benchmark,
            sample.original_output,
            sample.answer
        )
        sample.accuracy_refined = self.accuracy_evaluator.evaluate(
            sample.benchmark,
            sample.refined_output,
            sample.answer
        )
        delta = sample.accuracy_refined - sample.accuracy_original
        if delta > 0:
            sample.refinement_helped = "improved"
        elif delta < 0:
            sample.refinement_helped = "regressed"
        else:
            sample.refinement_helped = "neutral"

        if sample.benchmark == "halueval":
            hallu_ref = sample.hallucinated_answer or sample.metadata.get("hallucinated_answer")
            sample.hallucination_original = self.accuracy_evaluator.detect_hallucination(
                sample.original_output, sample.answer, hallu_ref
            )
            sample.hallucination_refined = self.accuracy_evaluator.detect_hallucination(
                sample.refined_output, sample.answer, hallu_ref
            )
        
        # Log to wandb
        if self.use_wandb and wandb.run:
            wandb.log({
                "sample/accuracy_original": sample.accuracy_original,
                "sample/accuracy_refined": sample.accuracy_refined,
                "sample/refinement_delta": delta,
                "sample/latency_refinement_ms": sample.latency_refinement_ms,
                "sample/latency_qa_ms": (sample.latency_qa_original_ms + sample.latency_qa_refined_ms) / 2,
                "sample/semantic_drift": sample.semantic_drift,
                "sample/tokens_total": sample.tokens_refinement + sample.tokens_qa_original + sample.tokens_qa_refined,
                "sample/tokens_refinement": sample.tokens_refinement,
                "sample/cost_refinement": sample.cost_refinement,
                "sample/cost": sample.cost_refinement + sample.cost_qa_original + sample.cost_qa_refined,
                "sample/refinement_helped": 1 if sample.refinement_helped == "improved" else 0,
                **({"sample/hallucination_refined": int(sample.hallucination_refined)} if sample.hallucination_refined is not None else {})
            })
        
        return sample
    
    async def evaluate_benchmark(
        self,
        benchmark_name: str,
        max_samples: int = -1,
        batch_size: int = 10
    ) -> List[EvaluationSample]:
        """Evaluate a full benchmark."""
        print(f"\n{'='*80}")
        print(f"EVALUATING: {benchmark_name.upper()}")
        print(f"{'='*80}\n")
        
        # Load samples
        samples = self.loader.load_benchmark(benchmark_name, max_samples)
        print(f"Loaded {len(samples)} samples")
        
        # Evaluate in batches
        results = []
        for i in range(0, len(samples), batch_size):
            batch = samples[i:i+batch_size]
            batch_results = await asyncio.gather(*[
                self.evaluate_sample(sample, f"{benchmark_name}_{i+j}")
                for j, sample in enumerate(batch)
            ])
            results.extend(batch_results)
            
            # Progress update
            progress_pct = len(results) / len(samples) * 100
            print(f"Progress: {len(results)}/{len(samples)} samples ({progress_pct:.1f}%)")
            
            # Log benchmark progress to wandb
            if self.use_wandb and wandb.run:
                wandb.log({
                    f"{benchmark_name}/progress": len(results),
                    f"{benchmark_name}/progress_pct": progress_pct,
                })
        
        # Save results
        self.save_results(benchmark_name, results)
        
        # Log benchmark summary to wandb
        summary = self.generate_summary(benchmark_name, results)
        if self.use_wandb and wandb.run:
            wandb.log({
                f"{benchmark_name}/accuracy_original": summary["accuracy_original"],
                f"{benchmark_name}/accuracy_refined": summary["accuracy_refined"],
                f"{benchmark_name}/avg_latency_ms": summary["avg_latency_refinement_ms"],
                f"{benchmark_name}/avg_drift": summary["avg_semantic_drift"],
                f"{benchmark_name}/total_cost": summary["total_cost"],
                f"{benchmark_name}/help_rate": summary.get("refinement_help_rate", 0.0),
                f"{benchmark_name}/regress_rate": summary.get("refinement_regress_rate", 0.0),
            })
        
        return results
    
    def save_results(self, benchmark_name: str, results: List[EvaluationSample]):
        """Save evaluation results."""
        output_file = self.results_dir / f"{benchmark_name}_results.jsonl"
        
        with open(output_file, "w") as f:
            for sample in results:
                f.write(json.dumps(asdict(sample)) + "\n")
        
        print(f"\n✅ Results saved to: {output_file}")
    
    def generate_summary(self, benchmark_name: str, results: List[EvaluationSample]) -> Dict:
        """Generate summary statistics."""
        if not results:
            return {}
        
        total = len(results)
        
        summary = {
            "benchmark": benchmark_name,
            "total_samples": total,
            "accuracy_original": sum(r.accuracy_original for r in results) / total,
            "accuracy_refined": sum(r.accuracy_refined for r in results) / total,
            "avg_latency_refinement_ms": sum(r.latency_refinement_ms for r in results) / total,
            "avg_latency_qa_ms": sum(r.latency_qa_original_ms + r.latency_qa_refined_ms for r in results) / total / 2,
            "avg_tokens_refinement": sum(r.tokens_refinement for r in results) / total,
            "avg_tokens_qa": sum(r.tokens_qa_original + r.tokens_qa_refined for r in results) / total / 2,
            "total_cost": sum(r.cost_refinement + r.cost_qa_original + r.cost_qa_refined for r in results),
            "avg_semantic_drift": sum(r.semantic_drift for r in results) / total,
            "worker_utilization": self._calculate_worker_utilization(results)
        }
        summary.update(self._calculate_refinement_outcomes(results))
        if benchmark_name == "halueval":
            summary.update(self._calculate_hallucination_stats(results))
        
        return summary
    
    def _calculate_worker_utilization(self, results: List[EvaluationSample]) -> Dict:
        """Calculate worker utilization statistics."""
        worker_counts = {}
        for result in results:
            for worker in result.workers_used:
                worker_counts[worker] = worker_counts.get(worker, 0) + 1
        
        total = len(results)
        return {
            worker: count / total
            for worker, count in worker_counts.items()
        }

    def _calculate_refinement_outcomes(self, results: List[EvaluationSample]) -> Dict[str, Any]:
        """Calculate refinement outcome rates."""
        counts = {"improved": 0, "regressed": 0, "neutral": 0}
        for result in results:
            label = result.refinement_helped or "neutral"
            if label not in counts:
                label = "neutral"
            counts[label] += 1
        total = len(results) or 1
        return {
            "refinement_helped": counts["improved"],
            "refinement_regressed": counts["regressed"],
            "refinement_neutral": counts["neutral"],
            "refinement_help_rate": counts["improved"] / total,
            "refinement_regress_rate": counts["regressed"] / total,
            "refinement_neutral_rate": counts["neutral"] / total,
        }

    def _calculate_hallucination_stats(self, results: List[EvaluationSample]) -> Dict[str, Any]:
        total = len(results) or 1
        hallu_orig = sum(1 for r in results if r.hallucination_original)
        hallu_refined = sum(1 for r in results if r.hallucination_refined)
        return {
            "hallucination_rate_original": hallu_orig / total,
            "hallucination_rate_refined": hallu_refined / total
        }


async def main():
    """Main evaluation entry point."""
    data_dir = Path(__file__).parent / "data"
    results_dir = Path(__file__).parent / "results"
    
    evaluator = PRaaSEvaluator(data_dir, results_dir)
    
    # Test on small subset first
    benchmarks = ["bbh", "truthfulqa", "gsm8k", "commonsenseqa", "strategyqa", "halueval"]
    
    for benchmark in benchmarks:
        results = await evaluator.evaluate_benchmark(benchmark, max_samples=10)
        summary = evaluator.generate_summary(benchmark, results)
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: {benchmark.upper()}")
        print(f"{'='*80}")
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

