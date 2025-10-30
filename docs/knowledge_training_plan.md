# 🧠 Knowledge Enhancement Fine-tuning - Ready to Go!

## 📊 **Overview**

After paraphrasing models complete, we'll fine-tune on **knowledge-based datasets** to enhance:
- Entity understanding (Wikidata)
- Comprehensive knowledge (Wikipedia)
- Knowledge-grounded dialogue (KILT)

---

## 📁 **Datasets**

### 1. **Wikidata Descriptions** (`masaki-sakata/wikidata_descriptions`)
- **Purpose**: Entity definitions and descriptions
- **Format**: "What is [entity]?" → "[description]"
- **Sample Size**: 50,000 examples
- **Example**:
  ```
  Q: What is Python?
  A: Python is a high-level, interpreted programming language...
  ```

### 2. **Wikipedia** (`wikimedia/wikipedia`)
- **Purpose**: Comprehensive knowledge on topics
- **Format**: "Tell me about [topic]" → "[article summary]"
- **Sample Size**: 20,000 articles
- **Example**:
  ```
  Q: Tell me about Machine Learning.
  A: Machine learning is a branch of artificial intelligence...
  ```

### 3. **KILT - Wizard of Wikipedia** (`facebook/kilt_tasks`)
- **Purpose**: Knowledge-grounded conversational responses
- **Format**: Conversational Q&A with knowledge
- **Sample Size**: 30,000 dialogues
- **Example**:
  ```
  Q: I love science fiction movies!
  A: Science fiction is a fascinating genre that explores...
  ```

### **Combined Dataset**
- **Total**: ~100,000 high-quality knowledge examples
- **Format**: Chat-based (system + user + assistant)
- **File**: `/home/data/knowledge_combined.json`

---

## 🚀 **Preparation & Training Pipeline**

### **Step 1: Prepare Datasets** (Run after paraphrasing completes)
```bash
chmod +x /home/prepare_all_knowledge_datasets.sh
/home/prepare_all_knowledge_datasets.sh
```

**What it does:**
1. Downloads and processes Wikidata (50k examples)
2. Downloads and processes Wikipedia (20k articles)
3. Downloads and processes KILT WoW (30k dialogues)
4. Combines into single dataset (~100k examples)
5. Updates LLaMA-Factory configuration

**Expected Time**: 30-60 minutes

---

### **Step 2: Start Fine-tuning** (Parallel on both GPUs)

#### **Llama 3.2 3B** (GPU 0)
```bash
chmod +x /home/run_llama32_3b_knowledge_training.sh
nohup /home/run_llama32_3b_knowledge_training.sh > /home/llama32_3b_knowledge_training.log 2>&1 &
```

#### **Llama 3.1 8B** (GPU 1)
```bash
chmod +x /home/run_llama31_8b_knowledge_training.sh
nohup /home/run_llama31_8b_knowledge_training.sh > /home/llama31_8b_knowledge_training.log 2>&1 &
```

**Expected Training Time**: ~6-8 hours per model (can run in parallel!)

---

## ⚙️ **Training Configuration**

### Common Parameters
- **Method**: LoRA (rank=16, alpha=32)
- **Epochs**: 3
- **Learning Rate**: 2e-4
- **Validation Split**: 5% automatic
- **Evaluation**: Every 100 steps
- **Checkpointing**: Every 100 steps

### Model-Specific
| Parameter | 3B Model | 8B Model |
|-----------|----------|----------|
| Batch Size | 4 | 2 |
| Gradient Accumulation | 4 | 8 |
| Effective Batch Size | 16 | 16 |
| GPU | cuda:0 | cuda:1 |

---

## 📊 **Expected Outcomes**

After training, models will have enhanced:
1. ✅ **Entity Knowledge**: Better understanding of entities and their descriptions
2. ✅ **Topic Knowledge**: Comprehensive information on various subjects
3. ✅ **Conversational Knowledge**: Ability to engage in knowledge-grounded dialogue
4. ✅ **Q&A Abilities**: Improved question-answering with accurate information

---

## 🎯 **Complete Model Collection**

After all training completes, you'll have:

| Model | Task | Location |
|-------|------|----------|
| **Llama 3.2 3B** | Grammar Correction | `/home/models/llama32_3b_lora_factory` |
| **Llama 3.2 3B** | Paraphrasing | `/home/models/llama32_3b_paraphrase_lora` |
| **Llama 3.2 3B** | Knowledge | `/home/models/llama32_3b_knowledge_lora` |
| **Llama 3.1 8B** | Grammar Correction | `/home/models/llama31_8b_lora_factory` |
| **Llama 3.1 8B** | Paraphrasing | `/home/models/llama31_8b_paraphrase_lora` |
| **Llama 3.1 8B** | Knowledge | `/home/models/llama31_8b_knowledge_lora` |

**Total**: 6 specialized models! 🎉

---

## 📁 **Files Created**

### Dataset Preparation
- `/home/prepare_knowledge_datasets.py` - Main dataset processor
- `/home/prepare_all_knowledge_datasets.sh` - Wrapper script
- `/home/data/wikidata_knowledge.jsonl` - Wikidata processed
- `/home/data/wikipedia_knowledge.jsonl` - Wikipedia processed
- `/home/data/kilt_wow_knowledge.jsonl` - KILT processed
- `/home/data/knowledge_combined.json` - Combined dataset

### Training Configuration
- `/home/llama32_3b_knowledge_config.yaml` - 3B config
- `/home/llama31_8b_knowledge_config.yaml` - 8B config
- `/home/run_llama32_3b_knowledge_training.sh` - 3B runner
- `/home/run_llama31_8b_knowledge_training.sh` - 8B runner

---

## 🔍 **Monitoring**

### W&B Dashboard
**Project**: `knowledge-llama-enhancement`  
**URL**: https://wandb.ai/jshim0978/knowledge-llama-enhancement

### Progress Tracking
```bash
# Check 3B progress
tail -f /home/llama32_3b_knowledge_training.log | grep "%"

# Check 8B progress
tail -f /home/llama31_8b_knowledge_training.log | grep "%"

# Check GPU usage
nvidia-smi
```

---

## ⏱️ **Complete Timeline**

| Phase | Duration | Status |
|-------|----------|--------|
| **Phase 1**: Grammar (JFLEG) | 1-2 hours | ✅ DONE |
| **Phase 2**: Paraphrasing (PAWS+QQP) | ~12 hours | 🔄 IN PROGRESS |
| **Phase 3**: Dataset Prep | ~1 hour | ⏳ READY |
| **Phase 4**: Knowledge Training | ~6-8 hours | ⏳ READY |

**Total Project Time**: ~20 hours for complete multi-task fine-tuning!

---

## 💡 **Why This Approach?**

### **Optimal Dataset Pruning**
- **Wikidata**: 50k out of millions (focused on quality entities)
- **Wikipedia**: 20k articles (filtered for informativeness)
- **KILT**: 30k dialogues (wizard of Wikipedia subset)
- **Result**: ~100k high-quality examples vs. millions of raw data

### **Benefits**
1. ✅ Faster training (6-8 hours vs. days)
2. ✅ Higher quality (curated examples)
3. ✅ Better balance (diverse knowledge sources)
4. ✅ Manageable size (fits in memory efficiently)

---

## 🎯 **Next Steps (After Paraphrasing Completes)**

1. **Prepare datasets**: Run `/home/prepare_all_knowledge_datasets.sh`
2. **Verify preparation**: Check `/home/data/knowledge_combined.json`
3. **Start training**: Launch both 3B and 8B in parallel
4. **Monitor**: W&B dashboard + log files
5. **Complete**: All 6 models ready for deployment!

---

## 📝 **Quick Start Commands (Copy-Paste Ready)**

```bash
# After paraphrasing completes, run these in sequence:

# 1. Prepare datasets
/home/prepare_all_knowledge_datasets.sh

# 2. Start 3B training (GPU 0)
nohup /home/run_llama32_3b_knowledge_training.sh > /home/llama32_3b_knowledge_training.log 2>&1 &

# 3. Start 8B training (GPU 1)
nohup /home/run_llama31_8b_knowledge_training.sh > /home/llama31_8b_knowledge_training.log 2>&1 &

# 4. Monitor progress
tail -f /home/llama32_3b_knowledge_training.log
```

---

**🎉 Everything is ready! Just run these scripts after paraphrasing completes!**

**Rules used**: [JW-Global, MPR-Detected: no]

