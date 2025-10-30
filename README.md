# 🚀 Llama Fine-Tuning Project

Complete fine-tuning pipeline for Llama 3.2 3B and Llama 3.1 8B models across multiple tasks.

---

## 📊 Project Overview

This repository contains scripts and configurations for fine-tuning Llama models on three specialized tasks:

| Task | Dataset | Models | Status |
|------|---------|--------|--------|
| **Grammar Correction** | JFLEG (6,012 samples) | 3B, 8B | ✅ Complete |
| **Paraphrasing** | PAWS + QQP (143,658 samples) | 3B, 8B | ✅ Complete |
| **Knowledge Enhancement** | Wikipedia + KILT (37,529 samples) | 3B, 8B | ✅ Complete |

**Total**: 6 specialized fine-tuned models

---

## 📁 Repository Structure

```
/home/
├── configs/                    # Training configurations
│   ├── grammar/               # JFLEG grammar correction
│   ├── paraphrase/            # Paraphrasing tasks
│   ├── knowledge/             # Knowledge enhancement
│   └── dataset_comparison/    # PAWS-only vs QQP-only
│
├── scripts/                   # All working scripts
│   ├── dataset_prep/         # Dataset preparation
│   ├── training/             # Training launchers
│   ├── evaluation/           # Model evaluation
│   └── monitoring/           # Training monitoring
│
├── docs/                      # Documentation
├── logs/                      # Training logs
├── models/                    # Fine-tuned models
├── data/                      # Processed datasets
└── archive/                   # Deprecated files
```

---

## 🎯 Quick Start

### 1. Evaluate Trained Models

Test all 6 fine-tuned models on grammar, paraphrase, and knowledge tasks:

```bash
/home/scripts/evaluation/run_evaluation.sh
```

**Time**: ~30-45 minutes  
**Output**: Side-by-side comparisons of original vs fine-tuned models

### 2. Train New Models

#### Grammar Correction (JFLEG)
```bash
# 3B model
/home/scripts/training/train_3b_grammar.sh

# 8B model
/home/scripts/training/train_8b_grammar.sh
```

#### Paraphrasing (PAWS + QQP)
```bash
# 3B model
/home/scripts/training/train_3b_paraphrase.sh

# 8B model
/home/scripts/training/train_8b_paraphrase.sh
```

#### Knowledge Enhancement (Wikipedia + KILT)
```bash
# 3B model
/home/scripts/training/train_3b_knowledge.sh

# 8B model
/home/scripts/training/train_8b_knowledge.sh
```

### 3. Dataset Comparison Training

Compare PAWS-only vs QQP-only performance:

```bash
/home/scripts/training/start_dataset_comparison.sh
```

---

## 📚 Documentation

### Essential Documents
- **Main README**: This file (project overview)
- **Quick Reference**: `QUICK_REFERENCE.txt` - Common commands cheat sheet

### Evaluation & Results
- **🎯 Full Evaluation Report**: `docs/EVALUATION_REPORT_FOR_COLLEAGUES.md` - 30-page technical report
- **⚡ Quick Visual Summary**: `docs/QUICK_VISUAL_SUMMARY.md` - 5-minute presentation
- **📊 Comparison Spreadsheet**: `docs/model_comparison.csv` - Excel/Google Sheets import

### Deployment & Setup
- **Multi-Node Deployment**: `docs/multi_node_deployment.md` - Git sync and model transfer
- **Deployment Plan**: `docs/deployment_plan.md` - Server assignments
- **Evaluation Guide**: `docs/evaluation_guide.md` - How to run evaluations
- **Dataset Comparison Plan**: `docs/dataset_comparison_plan.md` - PAWS vs QQP analysis

---

## 📚 Configuration Files

All training configurations use LLaMA-Factory with LoRA:

| Config | Path | Description |
|--------|------|-------------|
| **Grammar** | `configs/grammar/` | JFLEG fine-tuning |
| **Paraphrase** | `configs/paraphrase/` | Combined PAWS+QQP |
| **Knowledge** | `configs/knowledge/` | Wikipedia+KILT |
| **Comparison** | `configs/dataset_comparison/` | Individual datasets |

### LoRA Configuration
- **Rank**: 16
- **Alpha**: 32
- **Dropout**: 0.05
- **Target**: All linear layers
- **Learning Rate**: 2e-4
- **Epochs**: 3

---

## 🔧 Dataset Preparation

### Prepare All Datasets

```bash
# JFLEG (Grammar)
python3 /home/scripts/dataset_prep/prep_jfleg.py

# PAWS + QQP (Paraphrasing)
/home/scripts/dataset_prep/run_all_paraphrase_prep.sh

# Wikipedia + KILT (Knowledge)
/home/scripts/dataset_prep/run_all_knowledge_prep.sh
```

### Dataset Formats

All datasets are converted to LLaMA-Factory's chat format:

```json
{
  "messages": [
    {"role": "user", "content": "Input text"},
    {"role": "assistant", "content": "Target output"}
  ]
}
```

---

## 📊 Model Evaluation

### Quick Evaluation (10 samples per task)

```bash
/home/scripts/evaluation/run_evaluation.sh
```

### Full Evaluation (100 samples per task)

Edit `/home/scripts/evaluation/evaluate_all_models.py`:
- Change lines 71, 126, 181
- From: `test_subset = test_samples[:10]`
- To: `test_subset = test_samples`

Then run the evaluation script.

### View Results

```bash
# Interactive viewer
python3 /home/scripts/evaluation/compare_results.py

# Read report
cat /home/evaluation_comparison_report.txt
```

---

## 🖥️ Hardware Requirements

- **GPU**: 2x NVIDIA L40 (46GB each)
- **Training**: ~19GB for 3B, ~28GB for 8B (with LoRA)
- **Inference**: ~6GB for 3B, ~16GB for 8B

### GPU Assignment
- **GPU 0**: Primary training (8B models)
- **GPU 1**: Secondary training (can run 3B + 8B simultaneously)

---

## 📈 Training Metrics

### Completed Training Results

| Model | Task | Train Loss | Eval Loss | Runtime |
|-------|------|------------|-----------|---------|
| 3B | Grammar | 1.79 | 2.17 | ~2h |
| 8B | Grammar | 1.54 | 2.04 | ~3h |
| 3B | Paraphrase | 0.46 | 0.57 | ~12h |
| 8B | Paraphrase | 0.46 | 0.57 | ~24h |
| 3B | Knowledge | 1.79 | 2.17 | ~4h |
| 8B | Knowledge | 1.54 | 2.04 | ~5h |

### W&B Dashboards

- **Grammar**: https://wandb.ai/jshim0978/jfleg-llama-lora-comparison
- **Paraphrase**: https://wandb.ai/jshim0978/paraphrase-llama-comparison
- **Knowledge**: https://wandb.ai/jshim0978/knowledge-llama-enhancement

---

## 🔍 Monitoring Training

### Check Status

```bash
/home/scripts/monitoring/check_status.sh
```

### Watch GPU Usage

```bash
watch -n 2 nvidia-smi
```

### Training Logs

```bash
# View live logs
tail -f /home/logs/grammar/3b_grammar_training.log
tail -f /home/logs/paraphrase/8b_paraphrase_training.log
tail -f /home/logs/knowledge/3b_knowledge_training.log

# All logs organized by task
ls /home/logs/grammar/      # Grammar correction logs
ls /home/logs/paraphrase/   # Paraphrasing logs
ls /home/logs/knowledge/    # Knowledge enhancement logs
ls /home/logs/monitoring/   # Training monitoring logs
```

---

## 📝 Documentation

| Document | Description |
|----------|-------------|
| `/home/docs/evaluation_guide.md` | Complete evaluation guide |
| `/home/docs/evaluation_quickstart.txt` | Quick evaluation reference |
| `/home/docs/dataset_comparison_plan.md` | Dataset comparison details |
| `/home/docs/knowledge_training_plan.md` | Knowledge training guide |
| `/home/docs/paraphrasing_summary.md` | Paraphrasing dataset info |

---

## 🎓 Key Scripts Reference

### Training
```bash
# Grammar
/home/scripts/training/train_{3b|8b}_grammar.sh

# Paraphrase
/home/scripts/training/train_{3b|8b}_paraphrase.sh

# Knowledge
/home/scripts/training/train_{3b|8b}_knowledge.sh

# Dataset Comparison
/home/scripts/training/train_{3b|8b}_{paws|qqp}_only.sh
```

### Evaluation
```bash
# Run evaluation
/home/scripts/evaluation/run_evaluation.sh

# View results
python3 /home/scripts/evaluation/compare_results.py
```

### Dataset Preparation
```bash
# Paraphrase datasets
/home/scripts/dataset_prep/run_all_paraphrase_prep.sh

# Knowledge datasets
/home/scripts/dataset_prep/run_all_knowledge_prep.sh
```

---

## 🛠️ Environment Setup

### Required Environment Variables

```bash
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export WANDB_API_KEY="your_key_here"
export CUDA_VISIBLE_DEVICES=0  # or 1
```

All training scripts set these automatically.

---

## 📦 Model Outputs

Trained models are saved in `/home/models/`:

```
/home/models/
├── llama32_3b_lora_factory/          # Grammar (3B)
├── llama31_8b_lora_factory/          # Grammar (8B)
├── llama32_3b_paraphrase_lora/       # Paraphrase (3B)
├── llama31_8b_paraphrase_lora/       # Paraphrase (8B)
├── llama32_3b_knowledge_lora/        # Knowledge (3B)
└── llama31_8b_knowledge_lora/        # Knowledge (8B)
```

Each contains:
- LoRA adapter weights
- Training checkpoints
- Configuration files
- Training plots

---

## 🚨 Troubleshooting

### Common Issues

**Out of Memory (OOM)**
- Reduce `per_device_train_batch_size` in config
- Increase `gradient_accumulation_steps`
- Use only one GPU: `export CUDA_VISIBLE_DEVICES=0`

**Slow Training**
- Check GPU utilization: `nvidia-smi`
- Verify `fp16: true` in config
- Ensure `gradient_checkpointing: true`

**W&B Not Logging**
- Check `WANDB_API_KEY` is set
- Verify `report_to: wandb` in config
- Check network connection

---

## 📊 Performance Benchmarks

### Training Speed (steps/sec)
- **3B**: ~0.5 steps/sec (batch=4, grad_acc=4)
- **8B**: ~0.3 steps/sec (batch=2, grad_acc=8)

### Memory Usage (fp16 + LoRA)
- **3B**: ~6-8GB
- **8B**: ~16-20GB

---

## 🔄 Version History

- **v1.0**: Initial fine-tuning (Grammar, Paraphrase, Knowledge)
- **v1.1**: Added dataset comparison (PAWS-only, QQP-only)
- **v1.2**: Comprehensive evaluation system
- **v1.3**: Repository organization and cleanup

---

## 📧 Support

For issues or questions:
- Check `/home/docs/` for detailed guides
- Review training logs in `/home/logs/`
- Inspect W&B dashboards for training metrics

---

## 📜 License

This project uses:
- **Llama Models**: Meta's Llama License
- **LLaMA-Factory**: Apache 2.0
- **Datasets**: Various (JFLEG, PAWS, QQP, Wikipedia, KILT)

---

**Last Updated**: October 27, 2025  
**Status**: All 6 models trained successfully  
**Next Steps**: Optional dataset comparison training

**Rules used**: [JW-Global, MPR-Detected: no]

