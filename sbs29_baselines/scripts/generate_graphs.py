#!/usr/bin/env python3
"""
Generate comprehensive results with full examples and graphs
"""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import defaultdict

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

results_dir = Path("/home/comparison/results_complete")
graphs_dir = Path("/home/comparison/graphs")
graphs_dir.mkdir(exist_ok=True)

print("="*80)
print("📊 GENERATING COMPREHENSIVE RESULTS WITH GRAPHS")
print("="*80)
print()

# Load all results
all_data = {}
datasets = ['truthfulqa', 'gsm8k', 'ambigqa', 'halueval']
frameworks = ['control', 'opro', 'promptagent', 'promptwizard']

for framework in frameworks:
    all_data[framework] = {}
    for dataset in datasets:
        file = results_dir / f"{framework}_{dataset}_COMPLETE.json"
        with open(file) as f:
            all_data[framework][dataset] = json.load(f)

# ========================================================================
# GRAPH 1: Average Latency by Framework and Dataset
# ========================================================================
print("📈 Generating Graph 1: Latency Comparison...")

fig, ax = plt.subplots(figsize=(14, 8))
x = np.arange(len(datasets))
width = 0.2

for i, framework in enumerate(frameworks):
    latencies = []
    for dataset in datasets:
        data = all_data[framework][dataset]
        avg_latency = sum(s['total_latency_ms'] for s in data) / len(data)
        latencies.append(avg_latency / 1000)  # Convert to seconds
    
    ax.bar(x + i * width, latencies, width, label=framework.upper())

ax.set_xlabel('Dataset', fontsize=12, fontweight='bold')
ax.set_ylabel('Average Total Latency (seconds)', fontsize=12, fontweight='bold')
ax.set_title('Average Total Latency by Framework and Dataset', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels([d.upper() for d in datasets])
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(graphs_dir / 'latency_comparison.png', dpi=300, bbox_inches='tight')
print(f"   ✅ Saved: {graphs_dir / 'latency_comparison.png'}")
plt.close()

# ========================================================================
# GRAPH 2: Token Usage by Framework and Dataset
# ========================================================================
print("📈 Generating Graph 2: Token Usage Comparison...")

fig, ax = plt.subplots(figsize=(14, 8))

for i, framework in enumerate(frameworks):
    tokens = []
    for dataset in datasets:
        data = all_data[framework][dataset]
        avg_tokens = sum(s['total_tokens'] for s in data) / len(data)
        tokens.append(avg_tokens)
    
    ax.bar(x + i * width, tokens, width, label=framework.upper())

ax.set_xlabel('Dataset', fontsize=12, fontweight='bold')
ax.set_ylabel('Average Total Tokens', fontsize=12, fontweight='bold')
ax.set_title('Average Token Usage by Framework and Dataset', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels([d.upper() for d in datasets])
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(graphs_dir / 'token_usage_comparison.png', dpi=300, bbox_inches='tight')
print(f"   ✅ Saved: {graphs_dir / 'token_usage_comparison.png'}")
plt.close()

# ========================================================================
# GRAPH 3: Latency Breakdown (Stacked Bar)
# ========================================================================
print("📈 Generating Graph 3: Latency Breakdown...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

for idx, dataset in enumerate(datasets):
    ax = axes[idx]
    
    refinement_times = []
    control_times = []
    refined_times = []
    
    for framework in frameworks:
        data = all_data[framework][dataset]
        refinement_times.append(sum(s['refinement_latency_ms'] for s in data) / len(data) / 1000)
        control_times.append(sum(s['control_generation_latency_ms'] for s in data) / len(data) / 1000)
        refined_times.append(sum(s['refined_generation_latency_ms'] for s in data) / len(data) / 1000)
    
    x_pos = np.arange(len(frameworks))
    
    p1 = ax.bar(x_pos, refinement_times, label='Refinement', color='#FF6B6B')
    p2 = ax.bar(x_pos, control_times, bottom=refinement_times, label='Control Gen', color='#4ECDC4')
    p3 = ax.bar(x_pos, refined_times, 
                bottom=np.array(refinement_times) + np.array(control_times),
                label='Refined Gen', color='#45B7D1')
    
    ax.set_ylabel('Time (seconds)', fontsize=10, fontweight='bold')
    ax.set_title(f'{dataset.upper()} - Latency Breakdown', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f.upper() for f in frameworks], rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(graphs_dir / 'latency_breakdown.png', dpi=300, bbox_inches='tight')
print(f"   ✅ Saved: {graphs_dir / 'latency_breakdown.png'}")
plt.close()

# ========================================================================
# GRAPH 4: Speedup vs Control
# ========================================================================
print("📈 Generating Graph 4: Speedup Factor...")

fig, ax = plt.subplots(figsize=(14, 8))

control_latencies = {}
for dataset in datasets:
    data = all_data['control'][dataset]
    control_latencies[dataset] = sum(s['total_latency_ms'] for s in data) / len(data)

for framework in ['opro', 'promptagent', 'promptwizard']:
    speedup_factors = []
    for dataset in datasets:
        data = all_data[framework][dataset]
        avg_latency = sum(s['total_latency_ms'] for s in data) / len(data)
        speedup = avg_latency / control_latencies[dataset]
        speedup_factors.append(speedup)
    
    ax.plot(datasets, speedup_factors, marker='o', linewidth=2, markersize=8, label=framework.upper())

ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Control Baseline')
ax.set_xlabel('Dataset', fontsize=12, fontweight='bold')
ax.set_ylabel('Slowdown Factor (×)', fontsize=12, fontweight='bold')
ax.set_title('Framework Slowdown vs Control Baseline', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xticks(range(len(datasets)))
ax.set_xticklabels([d.upper() for d in datasets])

plt.tight_layout()
plt.savefig(graphs_dir / 'speedup_comparison.png', dpi=300, bbox_inches='tight')
print(f"   ✅ Saved: {graphs_dir / 'speedup_comparison.png'}")
plt.close()

# ========================================================================
# GRAPH 5: Token Efficiency (Tokens per Second)
# ========================================================================
print("📈 Generating Graph 5: Token Efficiency...")

fig, ax = plt.subplots(figsize=(14, 8))

for i, framework in enumerate(frameworks):
    efficiency = []
    for dataset in datasets:
        data = all_data[framework][dataset]
        avg_tokens = sum(s['total_tokens'] for s in data) / len(data)
        avg_time_sec = sum(s['total_latency_ms'] for s in data) / len(data) / 1000
        efficiency.append(avg_tokens / avg_time_sec)
    
    ax.bar(x + i * width, efficiency, width, label=framework.upper())

ax.set_xlabel('Dataset', fontsize=12, fontweight='bold')
ax.set_ylabel('Tokens per Second', fontsize=12, fontweight='bold')
ax.set_title('Token Processing Efficiency by Framework and Dataset', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels([d.upper() for d in datasets])
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(graphs_dir / 'token_efficiency.png', dpi=300, bbox_inches='tight')
print(f"   ✅ Saved: {graphs_dir / 'token_efficiency.png'}")
plt.close()

print()
print("="*80)
print("✅ ALL GRAPHS GENERATED")
print("="*80)
print(f"Location: {graphs_dir}/")
print("Files:")
print("  1. latency_comparison.png - Average latency by framework/dataset")
print("  2. token_usage_comparison.png - Token usage by framework/dataset")
print("  3. latency_breakdown.png - Stacked breakdown of latency components")
print("  4. speedup_comparison.png - Slowdown factor vs control")
print("  5. token_efficiency.png - Tokens processed per second")
print()

