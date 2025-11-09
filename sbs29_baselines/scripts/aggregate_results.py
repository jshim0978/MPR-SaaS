#!/usr/bin/env python3
"""
Aggregate evaluation results and extract real examples
"""
import json
from pathlib import Path
from collections import defaultdict

results_dir = Path("/home/comparison/results_complete")
files = sorted(results_dir.glob("*.json"))

print("="*80)
print("📊 AGGREGATING RESULTS FROM 16 EVALUATION RUNS")
print("="*80)
print()

# Aggregate metrics by framework and dataset
aggregated = defaultdict(lambda: defaultdict(dict))
examples = {}

for file in files:
    framework, dataset = file.stem.replace("_COMPLETE", "").split("_", 1)
    
    with open(file) as f:
        data = json.load(f)
    
    # Calculate averages
    n_samples = len(data)
    
    avg_refinement_latency = sum(s['refinement_latency_ms'] for s in data) / n_samples
    avg_control_latency = sum(s['control_generation_latency_ms'] for s in data) / n_samples
    avg_refined_latency = sum(s['refined_generation_latency_ms'] for s in data) / n_samples
    avg_total_latency = sum(s['total_latency_ms'] for s in data) / n_samples
    
    avg_refinement_tokens = sum(s['refinement_tokens']['total'] for s in data) / n_samples
    avg_control_tokens = sum(s['control_generation_tokens']['total'] for s in data) / n_samples
    avg_refined_tokens = sum(s['refined_generation_tokens']['total'] for s in data) / n_samples
    avg_total_tokens = sum(s['total_tokens'] for s in data) / n_samples
    
    aggregated[framework][dataset] = {
        'n_samples': n_samples,
        'avg_refinement_latency_ms': avg_refinement_latency,
        'avg_control_latency_ms': avg_control_latency,
        'avg_refined_latency_ms': avg_refined_latency,
        'avg_total_latency_ms': avg_total_latency,
        'avg_refinement_tokens': avg_refinement_tokens,
        'avg_control_tokens': avg_control_tokens,
        'avg_refined_tokens': avg_refined_tokens,
        'avg_total_tokens': avg_total_tokens,
    }
    
    # Store first 3 examples from each run
    key = f"{framework}_{dataset}"
    examples[key] = data[:3]

# Print aggregated results
print("\n" + "="*80)
print("📈 EFFICIENCY METRICS (Latency in ms, Tokens)")
print("="*80)
print()

datasets = ['truthfulqa', 'gsm8k', 'ambigqa', 'halueval']
frameworks = ['control', 'opro', 'promptagent', 'promptwizard']

for dataset in datasets:
    print(f"\n{'='*80}")
    print(f"📊 {dataset.upper()}")
    print(f"{'='*80}")
    print()
    
    for framework in frameworks:
        metrics = aggregated[framework][dataset]
        print(f"{framework.upper():15s}:")
        print(f"  Samples:              {metrics['n_samples']:5d}")
        print(f"  Refinement Latency:   {metrics['avg_refinement_latency_ms']:8.1f} ms")
        print(f"  Control Latency:      {metrics['avg_control_latency_ms']:8.1f} ms")
        print(f"  Refined Latency:      {metrics['avg_refined_latency_ms']:8.1f} ms")
        print(f"  Total Latency:        {metrics['avg_total_latency_ms']:8.1f} ms")
        print(f"  Refinement Tokens:    {metrics['avg_refinement_tokens']:8.1f}")
        print(f"  Control Tokens:       {metrics['avg_control_tokens']:8.1f}")
        print(f"  Refined Tokens:       {metrics['avg_refined_tokens']:8.1f}")
        print(f"  Total Tokens:         {metrics['avg_total_tokens']:8.1f}")
        print()

# Save aggregated results
output_file = Path("/home/comparison/results_complete/AGGREGATED_METRICS.json")
with open(output_file, 'w') as f:
    json.dump(dict(aggregated), f, indent=2)

print(f"\n💾 Aggregated metrics saved to: {output_file}")
print()

# Print examples
print("\n" + "="*80)
print("📝 REAL EXAMPLES (First sample from each run)")
print("="*80)

for dataset in datasets:
    print(f"\n{'='*80}")
    print(f"DATASET: {dataset.upper()}")
    print(f"{'='*80}")
    
    for framework in frameworks:
        key = f"{framework}_{dataset}"
        sample = examples[key][0]
        
        print(f"\n{'─'*80}")
        print(f"FRAMEWORK: {framework.upper()}")
        print(f"{'─'*80}")
        
        print(f"\n📥 ORIGINAL PROMPT:")
        print(f"   {sample['original_prompt'][:150]}...")
        
        print(f"\n📤 REFINED PROMPT:")
        print(f"   {sample['refined_prompt'][:150]}...")
        
        print(f"\n🤖 CONTROL OUTPUT (LLM response to original):")
        print(f"   {sample['control_output'][:150]}...")
        
        print(f"\n✨ REFINED OUTPUT (LLM response to refined):")
        print(f"   {sample['refined_output'][:150]}...")
        
        print(f"\n📊 METRICS:")
        print(f"   Refinement: {sample['refinement_latency_ms']:.1f} ms, {sample['refinement_tokens']['total']} tokens")
        print(f"   Control:    {sample['control_generation_latency_ms']:.1f} ms, {sample['control_generation_tokens']['total']} tokens")
        print(f"   Refined:    {sample['refined_generation_latency_ms']:.1f} ms, {sample['refined_generation_tokens']['total']} tokens")
        print(f"   Total:      {sample['total_latency_ms']:.1f} ms, {sample['total_tokens']} tokens")

print("\n" + "="*80)
print("✅ AGGREGATION COMPLETE!")
print("="*80)

