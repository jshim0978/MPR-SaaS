# 🎯 EXACT REPLICATION GUIDE FOR JW1

## 📊 HaluEval Sampling Method

### What We Did:
We sampled **1,000 samples from 10,000** using Python's `random.sample()` with a **fixed seed (42)** for reproducibility.

---

## 🔄 METHOD 1: Use Our Exact Sampled File (RECOMMENDED)

### File Location:
```
/home/comparison/datasets/halueval_SAMPLED_1000.json
```

### Copy Command:
```bash
# If jw1 can access sbs29:
scp sbs29:/home/comparison/datasets/halueval_SAMPLED_1000.json ./

# Or transfer via shared storage
```

### Why This Method?
✅ **Guarantees 100% identical samples**  
✅ No risk of sampling mismatch  
✅ Simple and foolproof  

---

## 🔄 METHOD 2: Reproduce the Sampling (If File Transfer Not Possible)

### Python Code:
```python
import json
import random

# 1. Load full HaluEval dataset (10,000 samples)
with open('halueval_qa_data.jsonl') as f:
    full_data = json.load(f)

print(f"Loaded {len(full_data)} samples")  # Should be 10,000

# 2. Set fixed seed for reproducibility
random.seed(42)

# 3. Sample 1,000 items
sampled_data = random.sample(full_data, 1000)

print(f"Sampled {len(sampled_data)} samples")  # Should be 1,000

# 4. Save sampled data
with open('halueval_SAMPLED_1000.json', 'w') as f:
    json.dump(sampled_data, f, indent=2)

print("✅ Sampling complete!")
```

### Verification:
The first 5 sampled indices from the original 10,000 should be:
```
[1824, 409, 4506, 4012, 3657]
```

If these match, your sampling is correct!

---

## 📋 VERIFICATION CHECKLIST

### Sample 0 (Original Index 1824):
- **Question:** "Bebe Rexha was a singer who guested on the David Guetta song that was produced b..."
- **Knowledge:** "She is best known as a featured guest vocalist on several "Billboard" Hot 100 c..."

### Sample 1 (Original Index 409):
- **Question:** "Yukio Mishima and Roberto Bolaño, are Chilean?..."
- **Knowledge:** "Yukio Mishima (三島 由紀夫 , Mishima Yukio ) is the pen name of Kimitake Hiraoka..."

### Sample 2 (Original Index 4506):
- **Question:** "What Lindsey Stirling song's video received 1.3 million views on YouTube after o..."
- **Knowledge:** "Shatter Me" is a song composed and performed by American violinist Lindsey Stir..."

**If your first 3 samples match these, you're good to go!**

---

## 📊 FULL DATASET CONFIGURATION FOR FAIR COMPARISON

### All 4 Datasets (What We Evaluated):

| Dataset | File | Samples | Notes |
|---------|------|---------|-------|
| **TruthfulQA** | `truthfulqa_FULL_817.json` | 817 | Full dataset |
| **GSM8K** | `gsm8k_FULL_1319.json` | 1,319 | Full test set |
| **AmbigQA** | `ambigqa_FULL.json` | 2,002 | Full validation set |
| **HaluEval** | `halueval_SAMPLED_1000.json` | **1,000** | **Sampled with seed=42** |

### Why We Sampled HaluEval:
- Original: 10,000 samples
- With 4 frameworks × 10,000 = 40,000 evaluations just for HaluEval
- Would take ~30 additional days
- **Solution:** Sample 1,000 (10%) with fixed seed
- **Result:** Finished in 2.2 days instead of 22 days

---

## 🎯 FOR YOUR PRAAS EVALUATION

### What jw1 Should Run:

```python
# Pseudocode for PRaaS evaluation
frameworks_to_run = ["praas"]  # Your framework
datasets = {
    "truthfulqa": "truthfulqa_FULL_817.json",      # All 817
    "gsm8k": "gsm8k_FULL_1319.json",                # All 1,319
    "ambigqa": "ambigqa_FULL.json",                 # All 2,002
    "halueval": "halueval_SAMPLED_1000.json"        # Sampled 1,000 ⚠️
}

for dataset_name, dataset_file in datasets.items():
    # Load dataset
    data = load_dataset(dataset_file)
    
    # For each sample:
    for sample in data:
        original_prompt = sample['question']
        
        # 1. Refine with PRaaS
        refined_prompt = praas_refine(original_prompt)
        
        # 2. Generate control output (original → LLM)
        control_output = llama_generate(original_prompt)
        
        # 3. Generate refined output (refined → LLM)
        refined_output = llama_generate(refined_prompt)
        
        # 4. Save all data (same format as our baselines)
        save_result({
            "original_prompt": original_prompt,
            "refined_prompt": refined_prompt,
            "control_output": control_output,
            "refined_output": refined_output,
            # + all latency and token metrics
        })
```

### Critical Configuration (MUST MATCH):
```python
TARGET_LLM_CONFIG = {
    "model": "meta-llama/Llama-3.2-3B-Instruct",
    "temperature": 0.2,
    "top_p": 0.9,
    "max_new_tokens": 512,
    "do_sample": True,
    "seed": 13,  # For LLM generation
}

SAMPLING_SEED = 42  # For HaluEval sampling only
```

---

## 📁 OUTPUT FORMAT (MUST MATCH)

Save as: `praas_{dataset}_COMPLETE.json`

Example: `praas_halueval_COMPLETE.json`

Format: See `/home/comparison/DATA_COLLECTION_SPEC_FOR_JW1.md`

---

## ✅ VERIFICATION STEPS

1. **Load your sampled HaluEval**
2. **Check first 3 questions** match our Sample 0, 1, 2 above
3. **Run PRaaS evaluation** on all 4 datasets
4. **Compare sample counts:**
   - TruthfulQA: 817 ✓
   - GSM8K: 1,319 ✓
   - AmbigQA: 2,002 ✓
   - HaluEval: **1,000** ✓ (sampled, not 10,000!)
5. **Use same LLM config** (Llama-3.2-3B, temp=0.2, seed=13)

---

## 🚨 COMMON MISTAKES TO AVOID

❌ **Using full HaluEval (10,000)** instead of sampled (1,000)  
❌ **Random sampling without seed=42** (will get different samples)  
❌ **Different LLM config** (temperature, seed, etc.)  
❌ **Missing control outputs** (only saving refined outputs)  

✅ **Use halueval_SAMPLED_1000.json** (1,000 samples)  
✅ **Verify first 3 samples match** our verification checklist  
✅ **Same LLM config** (seed=13 for generation)  
✅ **Save both control and refined outputs**  

---

## 📞 QUESTIONS?

If anything is unclear:
1. Check `/home/comparison/DATA_COLLECTION_SPEC_FOR_JW1.md`
2. Look at our result files: `/home/comparison/results_complete/*_halueval_COMPLETE.json`
3. Verify your first 3 HaluEval samples match ours

---

## 📊 FINAL COMPARISON

After your PRaaS evaluation:

**Our Baselines (DONE):**
- `control_halueval_COMPLETE.json` (1,000 samples)
- `opro_halueval_COMPLETE.json` (1,000 samples)
- `promptagent_halueval_COMPLETE.json` (1,000 samples)
- `promptwizard_halueval_COMPLETE.json` (1,000 samples)

**Your PRaaS (TODO):**
- `praas_halueval_COMPLETE.json` (1,000 samples)

**Then:**
- GPT-5 judges all 5 frameworks on the **same 1,000 samples**
- Fair comparison! 🎯

---

**Key Point:** Use `halueval_SAMPLED_1000.json` with seed=42 for reproducibility!

**Rules used:** [JW-Global, MPR-Detected: yes]

