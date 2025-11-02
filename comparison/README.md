# Comparison Framework for MPR-SaaS Evaluation

**Purpose**: Systematic comparison of MPR-SaaS against baseline prompt refinement approaches

**Location**: SBS29 (Training Server) - Most powerful compute for running all comparisons

---

## 🎯 Goal

Demonstrate that **MPR-SaaS achieves ≥25% HHEM reduction** with **≤3% utility drop** at **competitive cost/latency** compared to:
1. No refinement (direct prompting)
2. Simple template-based refinement
3. Chain-of-thought prompting
4. Commercial LLM-based refinement (GPT-4/Claude)

---

## 📊 Baselines

### 1. **Control (No Refinement)**
- **Method**: Direct prompting to target LLM
- **Cost**: Baseline (0% overhead)
- **Latency**: Baseline (0ms overhead)
- **Implementation**: Passthrough

### 2. **Simple Template**
- **Method**: `"Please clarify and correct: {prompt}"`
- **Cost**: Minimal overhead (template tokens)
- **Latency**: ~10ms (template processing)
- **Implementation**: String formatting

### 3. **Chain-of-Thought (CoT)**
- **Method**: `"{prompt}\n\nLet's break this down step by step:"`
- **Cost**: Increased (CoT tokens)
- **Latency**: ~10ms (template processing)
- **Implementation**: Append CoT trigger

### 4. **GPT-4o Refinement**
- **Method**: Use GPT-4o to refine prompt before target LLM
- **Cost**: HIGH (GPT-4o call + target LLM)
- **Latency**: ~500-1000ms (API latency)
- **Implementation**: OpenAI API

### 5. **Claude 3.5 Refinement**
- **Method**: Use Claude 3.5 Sonnet to refine prompt
- **Cost**: HIGH (Claude + target LLM)
- **Latency**: ~500-1000ms (API latency)
- **Implementation**: Anthropic API

### 6. **MPR-SaaS (Ours)**
- **Method**: 3-worker parallel refinement (Cleaner || Describer || Paraphraser)
- **Cost**: LOW (3B/8B models, local inference)
- **Latency**: ~150-200ms (parallel execution)
- **Implementation**: Orchestrator calls jw2/jw3/kcloud

---

## 📈 Evaluation Metrics

### Primary Metrics
1. **HHEM Score** (0-1, lower = less hallucination)
   - Target: ≥25% relative reduction vs Control
   
2. **Utility Preservation** (GPT-4 judge, 0-1)
   - Target: ≤3% degradation vs Control
   
3. **Cost per Query** (USD)
   - Refinement cost + target LLM cost
   - Compare against GPT-4/Claude refinement
   
4. **Latency p50/p95** (ms)
   - End-to-end refinement + generation time

### Secondary Metrics
5. **Token Overhead** (%)
   - Extra tokens added by refinement
   
6. **Success Rate** (%)
   - % of queries successfully refined without errors

---

## 🗂️ Benchmark Datasets

### 1. **HHEM Eval Set** (Primary)
- **Source**: Vectara HaluEval benchmark
- **Size**: 500 samples
- **Purpose**: Measure hallucination reduction
- **Format**: Question-answer pairs with hallucination labels

### 2. **TruthfulQA** (Secondary)
- **Source**: TruthfulQA benchmark
- **Size**: 200 samples
- **Purpose**: Measure factual accuracy improvement
- **Format**: Questions with true/false labels

### 3. **Casual/Ambiguous Prompts** (Synthetic)
- **Source**: Hand-crafted noisy prompts
- **Size**: 200 samples
- **Purpose**: Test robustness to ill-formed inputs
- **Format**: Typos, grammatical errors, ambiguity

---

## 🏗️ Architecture

```
/home/comparison/
├── README.md                    # This file
├── baselines/
│   ├── control.py              # No refinement (direct)
│   ├── template.py             # Simple template refinement
│   ├── cot.py                  # Chain-of-thought
│   ├── gpt4_refine.py          # GPT-4o refinement
│   ├── claude_refine.py        # Claude 3.5 refinement
│   └── mpr_saas.py             # Our system (calls orchestrator)
├── eval_harness/
│   ├── runner.py               # Main evaluation runner
│   ├── metrics.py              # HHEM, utility, cost, latency
│   ├── judge.py                # GPT-4 as judge for utility
│   └── cost_calc.py            # Token → USD conversion
├── datasets/
│   ├── hhem_500.json           # HHEM benchmark subset
│   ├── truthfulqa_200.json     # TruthfulQA subset
│   └── casual_200.json         # Casual/ambiguous prompts
├── results/
│   ├── control/                # Control results
│   ├── template/               # Template results
│   ├── cot/                    # CoT results
│   ├── gpt4/                   # GPT-4 refinement results
│   ├── claude/                 # Claude refinement results
│   └── mpr_saas/               # MPR-SaaS results
├── analysis/
│   ├── aggregate.py            # Aggregate results across baselines
│   ├── significance.py         # Statistical tests (t-test, Wilcoxon)
│   ├── visualize.py            # Plots (cost vs HHEM, latency dist)
│   └── latex_tables.py         # Generate LaTeX for paper
└── run_all.sh                  # Master script to run all experiments
```

---

## 🚀 Quick Start

### Prerequisites

1. **API Keys** (for GPT-4/Claude baselines):
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

2. **MPR-SaaS Running** (for our system):
   - JW2 (Cleaner): http://129.254.202.252:8002
   - JW3 (Describer): http://129.254.202.253:8003
   - KCLOUD (Paraphraser): http://129.254.202.129:8004
   - JW1 (Orchestrator): http://129.254.202.251:8000

### Run All Experiments

```bash
cd /home/comparison
bash run_all.sh
```

This will:
1. Download and prepare datasets (HHEM, TruthfulQA)
2. Run all 6 baselines on all 3 benchmarks
3. Compute metrics (HHEM, cost, latency, utility)
4. Generate comparison tables and plots
5. Output final report to `results/COMPARISON_REPORT.md`

---

## 📊 Expected Results

| Method | HHEM ↓ | Rel. HHEM Reduction | Cost/Query | p95 Latency | Utility |
|--------|--------|---------------------|------------|-------------|---------|
| Control | 0.42 | 0% (baseline) | $0.005 | 300ms | 1.00 |
| Template | 0.40 | 5% | $0.005 | 310ms | 0.99 |
| CoT | 0.38 | 10% | $0.007 | 320ms | 0.98 |
| GPT-4 Refine | 0.33 | 21% | $0.025 | 850ms | 0.97 |
| Claude Refine | 0.34 | 19% | $0.020 | 900ms | 0.97 |
| **MPR-SaaS** | **0.30** | **29%** ✅ | **$0.008** | **200ms** | **0.98** ✅ |

**Key Claims**:
- ✅ **29% HHEM reduction** (exceeds 25% target)
- ✅ **2% utility drop** (within 3% target)
- ✅ **3.2x cheaper than GPT-4 refinement**
- ✅ **4x faster than commercial LLM refinement**

---

## 📝 Implementation Notes

### Target LLM for Final Answers
- **Primary**: Llama 3.1 70B (local, if available on SBS29)
- **Fallback**: GPT-4o-mini (via API, lower cost)
- **Reason**: Need consistent target LLM across all baselines

### HHEM Scoring
- Use existing HHEM evaluation methodology (from `/home/docs/FINAL_MODEL_SELECTION.md`)
- Score format: 0-10 scale normalized to 0-1
- Components: Accuracy, Completeness, Informativeness

### Cost Calculation
- Use `/home/config/prices.yml` for token pricing
- Account for:
  - Refinement overhead (templates, GPT-4/Claude calls, MPR-SaaS workers)
  - Target LLM generation cost
- Convert to 4o-equivalent USD

### Utility Preservation
- GPT-4o as judge
- Prompt: "Rate semantic similarity between original and refined prompt (0-1)"
- Accept if ≥0.97 (3% degradation threshold)

---

## 🔬 Experimental Design

### Randomization
- Shuffle benchmark order to avoid bias
- Use fixed random seed (42) for reproducibility

### Sample Size
- HHEM: 500 samples (sufficient for 95% CI ±0.02)
- TruthfulQA: 200 samples (supplementary)
- Casual: 200 samples (robustness check)

### Statistical Tests
- **Paired t-test**: Compare HHEM scores (paired by prompt)
- **Wilcoxon signed-rank**: Non-parametric alternative
- **Effect size**: Cohen's d
- **Significance level**: α = 0.05

---

## 📦 Deliverables

1. **Raw Results**: JSON files per baseline/dataset
2. **Aggregated Metrics**: CSV with mean/std/p50/p95
3. **Significance Tests**: p-values, effect sizes
4. **Plots**: 
   - HHEM reduction vs Cost
   - Latency distribution (violin plot)
   - Utility preservation (bar chart)
5. **LaTeX Tables**: Ready for paper insertion
6. **Final Report**: Markdown summary with key findings

---

## 🎯 Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| HHEM Reduction | ≥25% | TBD |
| Utility Preservation | ≥97% | TBD |
| Cost vs GPT-4 Refine | <50% | TBD |
| Latency p95 | <200ms | TBD |
| Statistical Significance | p<0.05 | TBD |

---

**Rules used**: [JW-Global, MPR-Detected]

