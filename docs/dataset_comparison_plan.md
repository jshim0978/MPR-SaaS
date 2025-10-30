# 📊 Paraphrase Dataset Comparison - Training Plan

## ✅ **Prepared and Ready!**

All scripts and configurations are ready for PAWS-only vs QQP-only comparison training.

---

## 📁 **Datasets Created**

| Dataset | Examples | Percentage | File |
|---------|----------|------------|------|
| **PAWS only** | 43,658 | 30% | `/home/data/paws_only.json` |
| **QQP only** | 100,000 | 70% | `/home/data/qqp_only.json` |
| **Combined** | 143,658 | 100% | (already training) |

---

## 🎯 **Training Schedule**

### **Phase 1: 3B Models** (Run in parallel)
```bash
# Option 1: Interactive launcher
/home/start_dataset_comparison_training.sh

# Option 2: Manual start
nohup /home/run_llama32_3b_paws_only.sh > /dev/null 2>&1 &  # GPU 0
nohup /home/run_llama32_3b_qqp_only.sh > /dev/null 2>&1 &   # GPU 1
```

**Estimated Time:**
- 3B PAWS: ~3 hours (GPU 0)
- 3B QQP: ~6 hours (GPU 1)
- **Total**: ~6 hours (parallel)

### **Phase 2: 8B Models** (Run after Phase 1 completes)
```bash
nohup /home/run_llama31_8b_paws_only.sh > /dev/null 2>&1 &  # GPU 0
nohup /home/run_llama31_8b_qqp_only.sh > /dev/null 2>&1 &   # GPU 1
```

**Estimated Time:**
- 8B PAWS: ~6 hours (GPU 0)
- 8B QQP: ~14 hours (GPU 1)
- **Total**: ~14 hours (parallel)

---

## 📊 **Complete Model Matrix**

After all training completes, you'll have:

| Model Size | Dataset | Status | Location |
|------------|---------|--------|----------|
| **3B** | Grammar (JFLEG) | ✅ Done | `llama32_3b_lora_factory/` |
| **3B** | Paraphrase (Combined) | ✅ Done | `llama32_3b_paraphrase_lora/` |
| **3B** | Paraphrase (PAWS) | ⏳ Ready | `llama32_3b_paws_only_lora/` |
| **3B** | Paraphrase (QQP) | ⏳ Ready | `llama32_3b_qqp_only_lora/` |
| **3B** | Knowledge | ⏳ Ready | `llama32_3b_knowledge_lora/` |
| **8B** | Grammar (JFLEG) | ✅ Done | `llama31_8b_lora_factory/` |
| **8B** | Paraphrase (Combined) | 🔄 Training | `llama31_8b_paraphrase_lora/` |
| **8B** | Paraphrase (PAWS) | ⏳ Ready | `llama31_8b_paws_only_lora/` |
| **8B** | Paraphrase (QQP) | ⏳ Ready | `llama31_8b_qqp_only_lora/` |
| **8B** | Knowledge | 🔄 Training | `llama31_8b_knowledge_lora/` |

**Total**: 10 specialized models!

---

## 🔗 **Monitoring**

### **W&B Projects**
- **Dataset Comparison**: https://wandb.ai/prml-nlp/paraphrase-dataset-comparison
- **Combined Training**: https://wandb.ai/prml-nlp/paraphrase-llama-comparison
- **Knowledge Training**: https://wandb.ai/prml-nlp/knowledge-llama-enhancement

### **Log Files**
```bash
# 3B Models
tail -f /home/llama32_3b_paws_only_training.log
tail -f /home/llama32_3b_qqp_only_training.log

# 8B Models
tail -f /home/llama31_8b_paws_only_training.log
tail -f /home/llama31_8b_qqp_only_training.log
```

---

## 📈 **Comparison Analysis Plan**

After training, you can analyze:

### 1. **Dataset Size Impact**
   - PAWS (43k) vs QQP (100k) vs Combined (143k)
   - Does more data = better performance?

### 2. **Dataset Quality**
   - PAWS: High-quality, adversarial paraphrases
   - QQP: Real-world question paraphrases
   - Which generalizes better?

### 3. **Model Size Impact**
   - 3B vs 8B on each dataset
   - Scaling behavior analysis

### 4. **Training Efficiency**
   - Loss curves comparison
   - Convergence speed
   - Evaluation metrics

---

## ⏱️ **Complete Timeline**

### **Currently Running** (Until Oct 25)
- 8B Knowledge: ~15:13 today
- 8B Paraphrase (Combined): ~09:30 tomorrow

### **Phase 1: Dataset Comparison** (After current completes)
- 3B PAWS + QQP: ~6 hours

### **Phase 2: 8B Dataset Comparison**
- 8B PAWS + QQP: ~14 hours

---

## 🚀 **Quick Start Commands**

### **Start Phase 1 Now** (if GPUs are free)
```bash
/home/start_dataset_comparison_training.sh
```

### **Manual Control**
```bash
# 3B PAWS (GPU 0)
/home/run_llama32_3b_paws_only.sh

# 3B QQP (GPU 1)
/home/run_llama32_3b_qqp_only.sh

# 8B PAWS (GPU 0)
/home/run_llama31_8b_paws_only.sh

# 8B QQP (GPU 1)
/home/run_llama31_8b_qqp_only.sh
```

---

## 📋 **Configuration Files**

All configs use consistent settings:
- LoRA: rank=16, alpha=32
- Epochs: 3
- Learning rate: 2e-4
- Evaluation: every 100 steps, 1% validation split
- W&B logging: enabled

Files:
- `/home/llama32_3b_paws_only_config.yaml`
- `/home/llama32_3b_qqp_only_config.yaml`
- `/home/llama31_8b_paws_only_config.yaml`
- `/home/llama31_8b_qqp_only_config.yaml`

---

**Everything is ready! Start when current trainings complete or when GPUs are available.** 🎯

