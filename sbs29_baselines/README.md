# SBS29 Baseline Evaluations

**Trainer Node:** sbs29  
**Evaluation Period:** November 7-9, 2025  
**Status:** ✅ Complete (20,552 samples, 100% success rate)

## 📊 Overview

This directory contains the complete baseline evaluation results for our EACL manuscript. We evaluated 4 prompt optimization frameworks (Control, OPRO, PromptAgent, PromptWizard) across 4 datasets (TruthfulQA, GSM8K, AmbigQA, HaluEval) using Llama-3.2-3B-Instruct as the target model.

## 📁 Directory Structure

```
sbs29_baselines/
├── README.md                    ← This file
├── EVALUATION_RESULTS.md        ← Detailed results summary
├── SBS29_results.zip            ← Complete results package (16 MB)
│
├── baselines/                   ← Baseline implementations
│   ├── opro_baseline.py         ← OPRO (Optimization by PROmpting)
│   ├── promptagent_baseline.py  ← PromptAgent (Strategic planning)
│   └── promptwizard_baseline.py ← PromptWizard (Mutation-based)
│
├── datasets/                    ← Evaluation datasets
│   ├── README.md                ← Dataset documentation
│   ├── truthfulqa_FULL_817.json ← 817 questions
│   ├── gsm8k_FULL_1319.json     ← 1,319 math problems
│   ├── ambigqa_FULL.json        ← 2,002 ambiguous questions
│   └── halueval_SAMPLED_1000.json ← 1,000 hallucination samples (seed=42)
│
├── docs/                        ← Documentation
│   ├── REPLICATION_GUIDE.md     ← How to replicate our evaluation
│   ├── DATA_COLLECTION_SPEC.md  ← Data format specification
│   └── QUICK_REFERENCE.txt      ← One-page quick reference
│
├── graphs/                      ← Visualizations (300 DPI PNG)
│   ├── latency_comparison.png
│   ├── token_usage_comparison.png
│   ├── latency_breakdown.png
│   ├── speedup_comparison.png
│   └── token_efficiency.png
│
└── scripts/                     ← Evaluation scripts
    ├── run_full_evaluation.py   ← Main evaluation runner
    ├── generate_graphs.py       ← Graph generation
    └── aggregate_results.py     ← Results aggregation
```

## 🎯 Quick Start

### 1. View Results

Extract and explore the complete results:

```bash
cd sbs29_baselines
unzip SBS29_results.zip
cat EVALUATION_RESULTS.md
```

### 2. Replicate Evaluation

See `docs/REPLICATION_GUIDE.md` for detailed instructions on replicating our evaluation on other servers (jw1, jw2, jw3, kcloud).

### 3. Generate Graphs

```bash
cd scripts
python3 generate_graphs.py
```

## 📊 Results Summary

### Frameworks Evaluated:
- **Control**: Baseline (no refinement)
- **OPRO**: 1-iteration optimization
- **PromptAgent**: Strategic planning
- **PromptWizard**: 3-round mutation

### Datasets Used:
- **TruthfulQA**: 817 samples
- **GSM8K**: 1,319 samples
- **AmbigQA**: 2,002 samples
- **HaluEval**: 1,000 samples (sampled with seed=42)

### Performance (average per sample):
| Framework | Latency (s) | Tokens | Slowdown | Token Overhead |
|-----------|-------------|--------|----------|----------------|
| Control | 17.0 | 641 | 1.00× | 1.00× |
| OPRO | 21.3 | 916 | 1.25× | 1.43× |
| PromptAgent | 26.7 | 1,100 | 1.57× | 1.72× |
| PromptWizard | 38.6 | 1,612 | 2.27× | 2.51× |

## 🔧 Configuration

**Target Model:** `meta-llama/Llama-3.2-3B-Instruct`  
**Decoding:**
- Temperature: 0.2
- Top-p: 0.9
- Max tokens: 512
- Seed: 13

## 📦 Complete Results Package

The `SBS29_results.zip` file (16 MB) contains:

- **10 detailed examples** with complete prompts and outputs
- **71 MB of raw JSON results** (20,552 samples)
- **5 publication-ready graphs** (300 DPI PNG)
- **Complete documentation** for replication
- **All datasets** used in evaluation

See the `README_FOR_ZIP.txt` inside the zip file for details.

## 🔄 For Other Servers

If you're running PRaaS evaluation on jw1, jw2, jw3, or kcloud:

1. **Use the same datasets** (especially `halueval_SAMPLED_1000.json`)
2. **Match the LLM config** (temperature, seed, etc.)
3. **Follow the data format** in `docs/DATA_COLLECTION_SPEC.md`
4. **Save results** in your own server directory (e.g., `/home/jw1_praas/`)

This ensures fair comparison and no git conflicts!

## 📚 Documentation

- **EVALUATION_RESULTS.md**: Detailed results summary with examples
- **docs/REPLICATION_GUIDE.md**: Step-by-step replication guide
- **docs/DATA_COLLECTION_SPEC.md**: JSON schema and data format
- **docs/QUICK_REFERENCE.txt**: One-page quick reference

## 🎓 Citation

If using these results in your manuscript:

```
Baseline evaluations conducted on sbs29 trainer node
November 7-9, 2025
Frameworks: Control, OPRO, PromptAgent, PromptWizard
Target Model: meta-llama/Llama-3.2-3B-Instruct
Datasets: TruthfulQA (817), GSM8K (1,319), AmbigQA (2,002), HaluEval (1,000)
```

## ✅ Verification

Before using these results:
- ✅ All 16 runs completed successfully
- ✅ 20,552 samples with complete data
- ✅ 100% success rate
- ✅ All metrics captured (latency, tokens, outputs)
- ✅ HaluEval sampled with seed=42 for reproducibility

## 📞 Questions?

See the documentation in `docs/` or the complete package in `SBS29_results.zip`.

---

**Generated:** November 10, 2025  
**Rules used:** [JW-Global, MPR-Detected: yes]

