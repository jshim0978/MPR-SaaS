# 🚀 Official Implementations - Full Benchmark Evaluation

**Fresh Start - Using ONLY Official Code with Llama-3.2-3B**

## 📋 Overview

This evaluation framework integrates **official implementations** of SOTA prompt refinement methods, all adapted to use the same base model (`meta-llama/Llama-3.2-3B`) for fair comparison.

### Methods Evaluated

1. **Control** (Baseline) - No refinement
2. **ADO** (Baseline) - Format normalization only
3. **OPRO-Official** - From `google-deepmind/opro`
4. **PromptAgent-Official** - From `XinyuanWangCS/PromptAgent`
5. **PromptBreeder-Official** - From `carperai/promptbreeder`
6. **ProTeGi-Official** - From `yongchao98/PROMST`
7. **CoVe-Official** - From `chain-of-verification`

### Benchmarks (FULL Datasets)

| Benchmark | Size | Description |
|-----------|------|-------------|
| **TruthfulQA** | 817 questions | Truthfulness and factuality |
| **HaluEval** | 10,000 samples | Hallucination detection (QA) |
| **GSM8K** | 1,319 questions | Grade school math reasoning |
| **AmbigQA** | 2,002 questions | Ambiguous question answering |

### Base Model

- **Model**: `meta-llama/Llama-3.2-3B`
- **Why**: Open-source, reproducible, fair comparison baseline
- **All methods use the same model** for refinement and answer generation

## 🎯 Quick Start

### Launch All Benchmarks (Recommended)

```bash
cd /home/comparison
./launch_all_official.sh
```

This will:
- Launch **all 4 benchmarks** simultaneously
- Utilize **both GPU 0 and GPU 1** via multiprocessing
- Log to separate files for each benchmark
- Save results to `results_official/`

### Monitor Progress

```bash
# Watch all logs
tail -f logs_*_official.log

# Check GPU usage
watch -n 1 nvidia-smi

# Check running processes
ps aux | grep run_.*_official
```

### Run Individual Benchmarks

```bash
# TruthfulQA (817 questions, ~2 hours)
python3 run_truthfulqa_official.py

# GSM8K (1,319 questions, ~3 hours)
python3 run_gsm8k_official.py

# AmbigQA (2,002 questions, ~5 hours)
python3 run_ambigqa_official.py

# HaluEval (10,000 samples, ~24 hours)
python3 run_halueval_official.py
```

## 📊 Expected Timeline

| Benchmark | Questions | Methods | Est. Time | Status |
|-----------|-----------|---------|-----------|--------|
| TruthfulQA | 817 | 7 | ~2 hours | ⏳ |
| GSM8K | 1,319 | 7 | ~3 hours | ⏳ |
| AmbigQA | 2,002 | 7 | ~5 hours | ⏳ |
| HaluEval | 10,000 | 7 | ~24 hours | ⏳ |

**Total**: All benchmarks will complete within ~24 hours (running in parallel).

## 📁 File Structure

```
/home/comparison/
├── official_unified_evaluation.py    # Core evaluation framework
├── run_truthfulqa_official.py        # TruthfulQA evaluation
├── run_halueval_official.py          # HaluEval evaluation
├── run_gsm8k_official.py             # GSM8K evaluation
├── run_ambigqa_official.py           # AmbigQA evaluation
├── launch_all_official.sh            # Master launch script
│
├── datasets/
│   ├── truthfulqa_FULL_817.json      # FULL TruthfulQA dataset
│   ├── halueval_qa_data.jsonl        # FULL HaluEval dataset (10k)
│   ├── gsm8k_FULL_1319.json          # FULL GSM8K dataset
│   └── ambigqa_FULL.json             # FULL AmbigQA dataset (2k)
│
├── official_repos/                    # Official implementation clones
│   ├── opro/                         # google-deepmind/opro
│   ├── PromptAgent/                  # XinyuanWangCS/PromptAgent
│   ├── PromptBreeder/                # carperai/promptbreeder
│   ├── PROMST/                       # yongchao98/PROMST
│   └── chain-of-verification/        # CoVe
│
└── results_official/                 # Results (created automatically)
    ├── truthfulqa_official_results.json
    ├── halueval_official_results.json
    ├── gsm8k_official_results.json
    └── ambigqa_official_results.json
```

## 🔧 Technical Details

### Parallel Execution Strategy

Each benchmark uses **multiprocessing** to split methods across GPUs:

- **GPU 0**: Control, ADO, OPRO, PromptAgent
- **GPU 1**: PromptBreeder, ProTeGi, CoVe

This ensures maximum GPU utilization and faster completion.

### WandB Integration

All runs log to **WandB** project: `mpr-official-comparison`

Metrics tracked:
- Latency (ms)
- Token usage (input + output)
- Success rate
- Progress (per method)

### Official Adaptations

Each official implementation has been adapted to:
1. Use `Llama-3.2-3B` instead of original models (PaLM-2, GPT-3.5, etc.)
2. Follow the same evaluation protocol
3. Return standardized `EvaluationResult` objects
4. Support parallel execution

## 📈 Result Format

Each result file contains JSON array of `EvaluationResult` objects:

```json
{
  "method": "OPRO-Official",
  "benchmark": "TruthfulQA",
  "original_prompt": "What is the capital of France?",
  "refined_prompt": "Please provide the capital city of France.",
  "generated_answer": "Paris",
  "latency_ms": 1234.56,
  "tokens_input": 50,
  "tokens_output": 10,
  "metadata": {
    "type": "official",
    "repo": "google-deepmind/opro",
    "meta_tokens_in": 30,
    "meta_tokens_out": 5
  },
  "error": null
}
```

## 🛑 Stopping Evaluation

If you need to stop all running evaluations:

```bash
pkill -f run_.*_official.py
```

## 🔍 Troubleshooting

### CUDA Out of Memory

If you encounter OOM errors:
1. Reduce batch size (currently 1)
2. Run benchmarks sequentially instead of parallel
3. Use only one GPU

### Import Errors

Ensure all CUDA libraries are in `LD_LIBRARY_PATH`:
```bash
export LD_LIBRARY_PATH=/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda/lib64:${LD_LIBRARY_PATH}
```

### Model Loading Issues

If model fails to load:
1. Check cache: `ls -lh /home/.cache/huggingface/hub/`
2. Check disk space: `df -h`
3. Re-download if needed: `rm -rf /home/.cache/huggingface/hub/models--meta-llama--Llama-3.2-3B`

## 📝 Notes

- **Rules Used**: [JW-Global] - Small focused diffs, safety, reproducibility
- **Manuscript Alignment**: All methods and benchmarks aligned with EACL_v01.pdf
- **Scientific Rigor**: FULL datasets used (not samples) for publication-grade results
- **Fair Comparison**: All methods use the same base model (Llama-3.2-3B)

## 🎓 Citation

If you use these official implementations:

- **OPRO**: Yang et al., 2023 - "Large Language Models as Optimizers"
- **PromptAgent**: Wang et al., 2024 - "PromptAgent: Strategic Planning with Language Models"
- **PromptBreeder**: Fernando et al., 2023 - "Promptbreeder: Self-Referential Self-Improvement"
- **ProTeGi**: Ramnath et al., 2023 - "PROMST: Textual Gradients for LLM Optimization"
- **CoVe**: Dhuliawala et al., 2023 - "Chain-of-Verification Reduces Hallucination"

---

**Status**: ✅ Ready to launch
**Last Updated**: 2025-11-05
**WandB Project**: `mpr-official-comparison`

