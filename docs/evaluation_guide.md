# 🎯 Model Evaluation Plan

## Overview

Comprehensive evaluation of all 6 fine-tuned models to verify training quality.

---

## What Will Be Tested

### 📝 Grammar Correction (JFLEG)
- **Models**: Original 3B, Fine-tuned 3B, Original 8B, Fine-tuned 8B
- **Test Set**: 10 grammatically incorrect sentences
- **Expected**: Fine-tuned models should produce more grammatically correct outputs

### 🔄 Paraphrasing (PAWS)
- **Models**: Original 3B, Fine-tuned 3B, Original 8B, Fine-tuned 8B
- **Test Set**: 10 sentences to paraphrase
- **Expected**: Fine-tuned models should produce better paraphrases while preserving meaning

### 🧠 Knowledge (Wizard of Wikipedia)
- **Models**: Original 3B, Fine-tuned 3B, Original 8B, Fine-tuned 8B
- **Test Set**: 10 knowledge-seeking questions
- **Expected**: Fine-tuned models should provide more detailed, structured responses

---

## How to Run

### Quick Start
```bash
/home/run_model_evaluation.sh
```

This will:
1. Load each model (original + fine-tuned)
2. Generate outputs for 10 test samples per task
3. Save results to JSON files
4. Display side-by-side comparison
5. Save comparison report to text file

### Estimated Time
- ~30-45 minutes total
- Each model takes ~3-5 minutes to load and generate

---

## Output Files

### JSON Results (Machine-readable)
- `/home/evaluation_results_grammar.json`
- `/home/evaluation_results_paraphrase.json`
- `/home/evaluation_results_knowledge.json`

### Human-Readable Report
- `/home/evaluation_comparison_report.txt`

---

## What to Look For

### ✅ Success Indicators

**Grammar Models:**
- Fine-tuned models fix grammatical errors
- Outputs are more fluent and natural
- Sentence structure is improved

**Paraphrase Models:**
- Fine-tuned models produce diverse paraphrases
- Meaning is preserved
- Outputs sound natural and varied

**Knowledge Models:**
- Fine-tuned models provide more structured responses
- Better organization (lists, clear points)
- More detailed and informative

### ⚠️ Warning Signs

- No difference between original and fine-tuned
- Fine-tuned model outputs are worse
- Outputs are repetitive or incoherent
- Responses are too short or truncated

---

## Sample Output Format

For each test sample, you'll see:

```
──────────────────────────────────────────────────────────────────────────
📝 Sample 1/10
──────────────────────────────────────────────────────────────────────────

🔹 INPUT:
   The dog run fast in the park.

🔹 REFERENCE:
   The dog runs fast in the park.

🤖 Original 3B:
   The dog runs quickly in the park.

🤖 Fine-tuned 3B (JFLEG):
   The dog runs fast in the park.

🤖 Original 8B:
   The dog runs fast in the park.

🤖 Fine-tuned 8B (JFLEG):
   The dog runs fast in the park.
```

---

## Next Steps After Evaluation

Based on results:

### If everything looks good ✅
- Models are ready for deployment/use
- Can proceed with dataset comparison training (PAWS-only vs QQP-only)
- Can run full 100-sample evaluation if needed

### If issues found ⚠️
- Investigate specific model problems
- Check training logs for anomalies
- Consider adjusting hyperparameters and retraining

---

## Quick Commands

### Run evaluation:
```bash
/home/run_model_evaluation.sh
```

### View results again:
```bash
python3 /home/compare_evaluation_results.py
```

### Check specific result file:
```bash
cat /home/evaluation_results_grammar.json | jq .
```

---

**Note**: Using 10 samples for quick verification. If you want the full 100-sample evaluation, edit `/home/evaluate_all_models.py` and change line 71 from `test_subset = test_samples[:10]` to `test_subset = test_samples` (do this in all three evaluation functions).

---

**Rules used**: [JW-Global, MPR-Detected: no]

