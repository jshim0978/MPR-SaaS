# Paraphrasing Fine-tuning Dataset Preparation - Complete

## 📊 Dataset Overview

Successfully prepared **PAWS** and **QQP** datasets for paraphrasing fine-tuning using **Option C: Bidirectional Generation**.

### Strategy: Bidirectional Paraphrase Generation

For each positive paraphrase pair (sentence1, sentence2), we create **2 training examples**:

1. **Direction 1**: `sentence1 → sentence2`
   - User: "Paraphrase this: [sentence1]"
   - Assistant: "[sentence2]"

2. **Direction 2**: `sentence2 → sentence1`
   - User: "Paraphrase this: [sentence2]"
   - Assistant: "[sentence1]"

This approach:
- ✅ Doubles the training data
- ✅ Teaches bidirectional paraphrasing
- ✅ Increases diversity of learning patterns

---

## 📈 Dataset Statistics

### PAWS Dataset (Google Research)
- **Source**: https://huggingface.co/datasets/google-research-datasets/paws
- **Quality**: High (human-annotated)
- **Focus**: Word-order variations, semantic similarity

| Split | Original Positive Pairs | Bidirectional Examples |
|-------|------------------------|------------------------|
| Train | 21,829 | 43,658 |
| Validation | 3,539 | 7,078 |
| Test | 3,536 | 7,072 |
| **Total** | **28,904** | **57,808** |

### QQP Dataset (Quora Question Pairs)
- **Source**: https://huggingface.co/datasets/AlekseyKorshuk/quora-question-pairs
- **Quality**: Good (noisy but diverse)
- **Focus**: Question paraphrasing, semantic equivalence
- **Limit**: 50,000 positive pairs (dataset is very large)

| Split | Original Positive Pairs | Bidirectional Examples |
|-------|------------------------|------------------------|
| Train | 50,000 | 100,000 |

### Combined Dataset

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Training Examples** | **143,658** | 100% |
| - From PAWS | 43,658 | 30.4% |
| - From QQP | 100,000 | 69.6% |
| **Validation Examples** | 7,078 | (PAWS only) |
| **Test Examples** | 7,072 | (PAWS only) |
| **Total for LLaMA-Factory** | 150,736 | (train + eval) |

---

## 📁 Output Files

All files saved in `/home/data/`:

1. **PAWS Files**:
   - `paws_paraphrase_train.jsonl` (43,658 examples)
   - `paws_paraphrase_eval.jsonl` (7,078 examples)
   - `paws_paraphrase_test.jsonl` (7,072 examples)

2. **QQP Files**:
   - `qqp_paraphrase_train.jsonl` (100,000 examples)

3. **Combined Files**:
   - `paraphrase_combined_train.jsonl` (143,658 examples)
   - `paraphrase_combined_eval.jsonl` (7,078 examples)
   - `paraphrase_combined_test.jsonl` (7,072 examples)
   - `paraphrase_combined.json` (150,736 examples - LLaMA-Factory format)

---

## ⚙️ Training Configuration

### Llama 3.2 3B Paraphrasing Config
- **File**: `/home/llama32_3b_paraphrase_config.yaml`
- **Output**: `/home/models/llama32_3b_paraphrase_lora`
- **Batch Size**: 4 per device
- **Gradient Accumulation**: 4 steps
- **Effective Batch Size**: 16
- **W&B Run**: `llama32-3b-paraphrase-lora`

### Llama 3.1 8B Paraphrasing Config
- **File**: `/home/llama31_8b_paraphrase_config.yaml`
- **Output**: `/home/models/llama31_8b_paraphrase_lora`
- **Batch Size**: 2 per device
- **Gradient Accumulation**: 8 steps
- **Effective Batch Size**: 16
- **W&B Run**: `llama31-8b-paraphrase-lora`

### Common Training Parameters
- **LoRA**: rank=16, alpha=32, dropout=0.05
- **Learning Rate**: 2e-4
- **Epochs**: 3
- **Scheduler**: Cosine with 10% warmup
- **Precision**: FP16
- **Gradient Clipping**: 1.0
- **Evaluation**: Every 100 steps
- **Checkpointing**: Every 100 steps

---

## 🚀 Next Steps

### 1. Start Training (Ready to Go!)

**For Llama 3.2 3B**:
```bash
cd /home
WANDB_API_KEY="your_wandb_key_here" \
WANDB_PROJECT="paraphrase-llama-comparison" \
HF_HOME="/home/hf_cache" \
TRANSFORMERS_CACHE="/home/hf_cache" \
LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH" \
CUDA_VISIBLE_DEVICES=0 \
llamafactory-cli train /home/llama32_3b_paraphrase_config.yaml
```

**For Llama 3.1 8B** (start after 3B completes):
```bash
cd /home
WANDB_API_KEY="your_wandb_key_here" \
WANDB_PROJECT="paraphrase-llama-comparison" \
HF_HOME="/home/hf_cache" \
TRANSFORMERS_CACHE="/home/hf_cache" \
LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib64:$LD_LIBRARY_PATH" \
CUDA_VISIBLE_DEVICES=0 \
llamafactory-cli train /home/llama31_8b_paraphrase_config.yaml
```

### 2. Expected Training Time
- **Llama 3.2 3B**: ~3-4 hours (143k examples, 3 epochs)
- **Llama 3.1 8B**: ~5-6 hours (143k examples, 3 epochs)

### 3. Monitoring
- **W&B Dashboard**: https://wandb.ai/jshim0978/paraphrase-llama-comparison
- **Local Logs**: `/home/models/llama32_3b_paraphrase_lora/` and `/home/models/llama31_8b_paraphrase_lora/`

---

## 🎯 Expected Results

After fine-tuning, the models should be able to:

1. ✅ Generate high-quality paraphrases
2. ✅ Maintain semantic meaning while varying word order
3. ✅ Handle both questions and statements
4. ✅ Produce diverse paraphrasing styles

**Use Cases**:
- Prompt cleaning and normalization
- Data augmentation
- Query expansion
- Text simplification/elaboration

---

## 📝 Notes

- PAWS provides high-quality, challenging examples with word-order variations
- QQP provides large-scale, diverse question paraphrasing examples
- Bidirectional training maximizes learning from each pair
- System prompt ensures models understand the paraphrasing task context

**Rules used**: [JW-Global, MPR-Detected: no]

