# Wikidata + Wikipedia Training (NO KILT WOW)

**Created**: October 29, 2025  
**Status**: Ready to train

## Rationale

After evaluating all 10 knowledge models, we found that:
- Fine-tuned models became MORE conversational (not factual/statistical as desired)
- KILT WOW dataset is dialogue-based, promoting conversational responses
- Wikidata and Wikipedia are more encyclopedic/factual

**Hypothesis**: Removing KILT WOW from the training mix will produce more factual, encyclopedic outputs.

---

## Dataset Composition

### New Combined Dataset: `knowledge_wikidata_wikipedia_only`

| Source | Samples | Characteristics |
|--------|---------|-----------------|
| **Wikidata** | 10,000 | Entity definitions, structured facts, relationships |
| **Wikipedia** | 14,982 | Comprehensive articles, contextual information, background |
| **Total** | **24,982** | Factual + encyclopedic (NO conversational dialogues) |

**File**: `/home/LLaMA-Factory/data/knowledge_wikidata_wikipedia_only.json`  
**Size**: 18.6 MB

### What's Excluded

❌ **KILT WOW** (Wizard of Wikipedia): 10,000 conversational dialogue samples

---

## Training Configuration

### Llama 3.2 3B

**Config**: `/home/configs/knowledge/3b_knowledge_wikidata_wikipedia_only.yaml`  
**Script**: `/home/scripts/training/train_3b_knowledge_wiki_only.sh`  
**Output**: `/home/models/llama32_3b_knowledge_wiki_only_lora`  
**GPU**: 0  
**W&B**: `knowledge-wikidata-wikipedia-only / llama32-3b-knowledge-wiki-only-lora`

**Parameters**:
- Batch size: 4
- Gradient accumulation: 4
- Effective batch: 16
- Learning rate: 2.0e-4
- Epochs: 3
- LoRA rank: 16

### Llama 3.1 8B

**Config**: `/home/configs/knowledge/8b_knowledge_wikidata_wikipedia_only.yaml`  
**Script**: `/home/scripts/training/train_8b_knowledge_wiki_only.sh`  
**Output**: `/home/models/llama31_8b_knowledge_wiki_only_lora`  
**GPU**: 1  
**W&B**: `knowledge-wikidata-wikipedia-only / llama31-8b-knowledge-wiki-only-lora`

**Parameters**:
- Batch size: 2
- Gradient accumulation: 8
- Effective batch: 16
- Learning rate: 2.0e-4
- Epochs: 3
- LoRA rank: 16

---

## Training Strategy

**Parallel Execution**:
- 3B on GPU 0
- 8B on GPU 1
- Both running simultaneously

**Estimated Time**:
- Based on previous knowledge training (24,982 samples):
  - 3B: ~2-3 hours
  - 8B: ~4-5 hours
- **Total**: ~4-5 hours (parallel execution)

---

## Evaluation Plan

After training completes:

1. **Quick Test**: Generate responses on a few samples to verify behavior
2. **Full Evaluation**: Run 20 samples with improved system prompt
3. **Comparison**: Compare with:
   - Original models (3B, 8B)
   - Combined dataset models (with KILT WOW)
   - Single-dataset models (Wikidata-only, Wikipedia-only)

**Expected Differences**:
- More factual/encyclopedic tone
- Less conversational/dialogue-style
- More structured information delivery

---

## Commands

### Start Training (Both GPUs in Parallel)
```bash
# GPU 0 (3B)
bash /home/scripts/training/train_3b_knowledge_wiki_only.sh &

# GPU 1 (8B)
bash /home/scripts/training/train_8b_knowledge_wiki_only.sh &

# Monitor
watch -n 1 nvidia-smi
```

### Monitor Logs
```bash
# 3B
tail -f /home/logs/knowledge_wiki_only/3b_training.log

# 8B
tail -f /home/logs/knowledge_wiki_only/8b_training.log
```

### Check W&B
```bash
wandb status
# Or visit: https://wandb.ai/jshim0978/knowledge-wikidata-wikipedia-only
```

---

## Success Criteria

✅ Training completes without errors  
✅ Models converge (eval_loss decreases)  
✅ W&B shows proper metrics  
✅ Generated outputs are more factual/encyclopedic  
✅ Less conversational than previous combined dataset models

---

## Next Steps After Training

1. Verify models load correctly
2. Generate test outputs
3. Compare with previous knowledge models
4. Update documentation with findings
5. Decide: Accept these results OR continue iterating

---

*This is an iterative experiment to improve factual output quality by removing conversational training data.*


