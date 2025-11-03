#!/usr/bin/env python3
"""
Quick Comparison Runner - Simple Baselines Only

Runs comparison on simple baselines that don't need vLLM.
This gives you immediate results while vLLM is being set up.
"""

import json
import time
import sys
import os
sys.path.insert(0, '/home/comparison')

from baselines.control import ControlBaseline
from baselines.template import TemplateBaseline  
from baselines.cot import CoTBaseline
from frameworks.ado.format_normalizer import ADO_FormatOnly


def load_dataset(filepath):
    """Load evaluation dataset"""
    with open(filepath, 'r') as f:
        return json.load(f)


def run_comparison(dataset_name, dataset, methods, max_samples=50):
    """Run comparison on dataset"""
    print(f"\n{'='*80}")
    print(f"EVALUATING: {dataset_name} ({min(max_samples, len(dataset))} samples)")
    print(f"{'='*80}\n")
    
    results = {method.name: [] for method in methods}
    
    for i, sample in enumerate(dataset[:max_samples]):
        if i % 10 == 0:
            print(f"Progress: {i}/{min(max_samples, len(dataset))}...")
        
        # Get original prompt
        if 'original_prompt' in sample:
            prompt = sample['original_prompt']
        elif 'noisy_prompt' in sample:
            prompt = sample['noisy_prompt']
        elif 'question' in sample:
            prompt = sample['question']
        else:
            continue
        
        # Run each method
        for method in methods:
            try:
                result = method.refine(prompt)
                results[method.name].append({
                    'sample_id': sample.get('id', i),
                    'original': prompt,
                    'refined': result.refined_prompt,
                    'latency_ms': result.latency_ms,
                    'tokens': result.tokens_used,
                    'cost': method.calculate_cost(result.tokens_used),
                    'error': result.error
                })
            except Exception as e:
                results[method.name].append({
                    'sample_id': sample.get('id', i),
                    'error': str(e)
                })
    
    return results


def compute_statistics(results):
    """Compute statistics for each method"""
    stats = {}
    
    for method_name, method_results in results.items():
        successful = [r for r in method_results if not r.get('error')]
        
        if not successful:
            stats[method_name] = {'error': 'No successful runs'}
            continue
        
        latencies = [r['latency_ms'] for r in successful]
        tokens = [r['tokens'] for r in successful]
        costs = [r['cost'] for r in successful]
        
        stats[method_name] = {
            'num_samples': len(successful),
            'avg_latency_ms': sum(latencies) / len(latencies),
            'p50_latency_ms': sorted(latencies)[len(latencies)//2],
            'p95_latency_ms': sorted(latencies)[int(len(latencies)*0.95)],
            'avg_tokens': sum(tokens) / len(tokens),
            'total_cost': sum(costs),
            'avg_cost_per_sample': sum(costs) / len(costs)
        }
    
    return stats


def print_comparison_table(stats):
    """Print comparison table"""
    print(f"\n{'='*80}")
    print("COMPARISON RESULTS")
    print(f"{'='*80}\n")
    
    print(f"{'Method':<25} {'Samples':<10} {'Avg Latency':<15} {'P95 Latency':<15} {'Avg Cost':<15}")
    print(f"{'-'*80}")
    
    for method_name, method_stats in stats.items():
        if 'error' in method_stats:
            print(f"{method_name:<25} {method_stats['error']}")
            continue
        
        print(f"{method_name:<25} "
              f"{method_stats['num_samples']:<10} "
              f"{method_stats['avg_latency_ms']:<15.3f}ms "
              f"{method_stats['p95_latency_ms']:<15.3f}ms "
              f"${method_stats['avg_cost_per_sample']:<14.6f}")
    
    print()


def save_results(results, stats, output_file):
    """Save results to JSON"""
    output = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'statistics': stats,
        'detailed_results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║            QUICK COMPARISON - SIMPLE BASELINES (NO vLLM NEEDED)          ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    
    # Initialize methods
    methods = [
        ControlBaseline(),
        TemplateBaseline(),
        CoTBaseline(),
        ADO_FormatOnly()
    ]
    
    print(f"Methods to evaluate: {[m.name for m in methods]}")
    
    # Load datasets
    datasets = {
        'HHEM': 'datasets/hhem_500.json',
        'TruthfulQA': 'datasets/truthfulqa_200.json',
        'Casual': 'datasets/casual_200.json'
    }
    
    all_stats = {}
    
    for dataset_name, filepath in datasets.items():
        print(f"\nLoading {dataset_name}...")
        try:
            dataset = load_dataset(filepath)
            print(f"✅ Loaded {len(dataset)} samples")
            
            # Run comparison (50 samples per dataset for quick results)
            results = run_comparison(dataset_name, dataset, methods, max_samples=50)
            
            # Compute statistics
            stats = compute_statistics(results)
            all_stats[dataset_name] = stats
            
            # Print results
            print_comparison_table(stats)
            
            # Save results
            output_file = f"results/quick_comparison_{dataset_name.lower()}.json"
            os.makedirs('results', exist_ok=True)
            save_results(results, stats, output_file)
            
        except FileNotFoundError:
            print(f"❌ Dataset not found: {filepath}")
        except Exception as e:
            print(f"❌ Error processing {dataset_name}: {e}")
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY ACROSS ALL DATASETS")
    print(f"{'='*80}\n")
    
    for dataset_name, stats in all_stats.items():
        print(f"\n{dataset_name}:")
        for method_name, method_stats in stats.items():
            if 'error' not in method_stats:
                print(f"  {method_name:<25} P95: {method_stats['p95_latency_ms']:.3f}ms | Cost: ${method_stats['avg_cost_per_sample']:.6f}")
    
    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}\n")
    print("1. Install vLLM: pip install vllm")
    print("2. Start vLLM: python3 -m vllm.entrypoints.openai.api_server \\")
    print("                --model meta-llama/Llama-3.2-3B-Instruct --port 8001")
    print("3. Run full comparison: python3 comparison/eval_harness/runner_local.py")
    print()


if __name__ == "__main__":
    main()

