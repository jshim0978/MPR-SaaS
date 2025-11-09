# Data Collection Specification for GPT-5 Judge Evaluation
**Version:** 1.0  
**Date:** November 7, 2025  
**Purpose:** Standardized data format for comparing prompt optimization frameworks

---

## 📋 Overview

This specification defines the **exact data format** that both evaluation systems (baseline frameworks on sbs29 and PRaaS framework on jw1) must collect to enable fair GPT-5 judge comparison.

---

## 🎯 Core Principle

For each sample, we capture **4 key pieces of data**:

1. **Original Prompt** - The input question/prompt from the dataset
2. **Refined Prompt** - The optimized version (or same as original for control)
3. **Control Output** - LLM's answer to the **original** prompt
4. **Refined Output** - LLM's answer to the **refined** prompt

This allows GPT-5 to judge: *"Which output is better: Control or Refined?"*

---

## 📊 JSON Output Format

### File Structure

Each evaluation run produces a **single JSON file** containing an **array of sample objects**.

**Filename Convention:**
```
{framework}_{dataset}_COMPLETE.json
```

Examples:
- `opro_truthfulqa_COMPLETE.json`
- `control_gsm8k_COMPLETE.json`
- `praas_halueval_COMPLETE.json`

### Sample Object Schema

Each sample in the array must contain these **exact fields**:

```json
{
  "sample_idx": 0,
  "dataset": "truthfulqa",
  "framework": "OPRO",
  "original_prompt": "Why are bananas yellow?",
  "refined_prompt": "Why are bananas, a fruit from trees, yellow in color?",
  "control_output": "Bananas are yellow because they contain carotenoids...",
  "refined_output": "Bananas are yellow due to the presence of carotenoids...",
  "refinement_latency_ms": 4500.5,
  "refinement_tokens": {
    "input": 76,
    "output": 178,
    "total": 254
  },
  "control_generation_latency_ms": 1200.3,
  "control_generation_tokens": {
    "input": 10,
    "output": 150,
    "total": 160
  },
  "refined_generation_latency_ms": 1300.7,
  "refined_generation_tokens": {
    "input": 15,
    "output": 155,
    "total": 170
  },
  "total_latency_ms": 6001.5,
  "total_tokens": 584
}
```

---

## 📝 Field Definitions

### **Required Fields (CRITICAL for GPT-5 Evaluation)**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `sample_idx` | integer | Sample index (0-based) | `0` |
| `dataset` | string | Dataset name | `"truthfulqa"` |
| `framework` | string | Framework name | `"OPRO"`, `"praas"`, `"control"` |
| `original_prompt` | string | **Original question/prompt from dataset** | `"Why are bananas yellow?"` |
| `refined_prompt` | string | **Optimized prompt from framework** | `"Why are bananas, a fruit, yellow?"` |
| `control_output` | string | **LLM answer to original_prompt** | `"Bananas are yellow because..."` |
| `refined_output` | string | **LLM answer to refined_prompt** | `"Bananas are yellow due to..."` |

### **Efficiency Metrics (for cost-benefit analysis)**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `refinement_latency_ms` | float | Time to refine prompt (ms) | `4500.5` |
| `refinement_tokens` | object | Tokens used in refinement | See below |
| `control_generation_latency_ms` | float | Time to generate control output | `1200.3` |
| `control_generation_tokens` | object | Tokens in control generation | See below |
| `refined_generation_latency_ms` | float | Time to generate refined output | `1300.7` |
| `refined_generation_tokens` | object | Tokens in refined generation | See below |
| `total_latency_ms` | float | Sum of all latencies | `6001.5` |
| `total_tokens` | integer | Sum of all tokens | `584` |

### **Token Object Structure**

```json
{
  "input": 76,    // Input tokens
  "output": 178,  // Output tokens
  "total": 254    // input + output
}
```

---

## 🔄 Evaluation Flow

### Step 1: Prompt Refinement
```
Input:  original_prompt
↓
Framework refines prompt
↓
Output: refined_prompt
        refinement_latency_ms
        refinement_tokens
```

**For Control Framework:**
- `refined_prompt = original_prompt` (no change)
- `refinement_latency_ms = 0`
- `refinement_tokens = {"input": 0, "output": 0, "total": 0}`

### Step 2: Control Output Generation
```
Input:  original_prompt
↓
Target LLM generates answer
↓
Output: control_output
        control_generation_latency_ms
        control_generation_tokens
```

### Step 3: Refined Output Generation
```
Input:  refined_prompt
↓
Target LLM generates answer
↓
Output: refined_output
        refined_generation_latency_ms
        refined_generation_tokens
```

---

## ⚙️ Target LLM Configuration

**CRITICAL:** Use the **same configuration** for fair comparison.

```python
TARGET_LLM = {
    "model": "meta-llama/Llama-3.2-3B-Instruct",
    "temperature": 0.2,
    "top_p": 0.9,
    "max_new_tokens": 512,
    "do_sample": True,
    "seed": 13,
}
```

**Important:**
- Use **same seed (13)** for reproducibility
- Apply to **both** control and refined output generation
- Do NOT change decoding parameters between samples

---

## 📂 Dataset Field Names

When loading datasets, extract prompts from these fields:

| Dataset | Prompt Field | Example |
|---------|-------------|---------|
| TruthfulQA | Direct string or `"question"` | `"Why are bananas yellow?"` |
| GSM8K | `"question"` | `"Janet's ducks lay 16 eggs..."` |
| AmbigQA | `"question"` | `"Who played the title role..."` |
| HaluEval | `"question"` | `"What is the capital of..."` |

---

## 🎨 Example: Complete Sample

```json
{
  "sample_idx": 42,
  "dataset": "gsm8k",
  "framework": "praas",
  "original_prompt": "Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?",
  "refined_prompt": "Janet's ducks lay 16 eggs per day. She consumes 3 for breakfast and uses 4 for muffins daily. Calculate her daily revenue at $2 per egg for the remaining eggs sold at the farmers' market.",
  "control_output": "## Step 1: Calculate total eggs used\nJanet uses 3 + 4 = 7 eggs daily.\n\n## Step 2: Calculate eggs sold\n16 - 7 = 9 eggs sold.\n\n## Step 3: Calculate revenue\n9 × $2 = $18\n\nThe answer is $18",
  "refined_output": "## Step 1: Calculate daily consumption\nBreakfast: 3 eggs, Muffins: 4 eggs = 7 eggs used\n\n## Step 2: Calculate remaining eggs\n16 total - 7 used = 9 eggs for market\n\n## Step 3: Calculate daily revenue\n9 eggs × $2/egg = $18\n\nThe answer is $18",
  "refinement_latency_ms": 3245.8,
  "refinement_tokens": {
    "input": 125,
    "output": 98,
    "total": 223
  },
  "control_generation_latency_ms": 8450.2,
  "control_generation_tokens": {
    "input": 67,
    "output": 142,
    "total": 209
  },
  "refined_generation_latency_ms": 8523.1,
  "refined_generation_tokens": {
    "input": 62,
    "output": 145,
    "total": 207
  },
  "total_latency_ms": 20219.1,
  "total_tokens": 639
}
```

---

## ✅ Validation Checklist

Before running full evaluation, verify:

- [ ] All required fields present
- [ ] `original_prompt` and `refined_prompt` are non-empty strings
- [ ] `control_output` and `refined_output` are non-empty strings
- [ ] All latency values are positive floats (in milliseconds)
- [ ] All token counts are non-negative integers
- [ ] Token totals match: `input + output = total`
- [ ] `total_latency_ms` = sum of 3 component latencies
- [ ] `total_tokens` = sum of 3 component token totals
- [ ] File is valid JSON (can be parsed)
- [ ] Array contains expected number of samples

---

## 🚫 Common Mistakes to Avoid

### ❌ **WRONG: Missing outputs**
```json
{
  "sample_idx": 0,
  "original_prompt": "Why are bananas yellow?",
  "refined_prompt": "Why are bananas yellow in color?",
  // Missing: control_output and refined_output
}
```

### ❌ **WRONG: Only efficiency metrics**
```json
{
  "sample_idx": 0,
  "latency_ms": 4500,
  "tokens_total": 254,
  // Missing: prompts and outputs
}
```

### ❌ **WRONG: Different LLM configs**
```python
# Control uses one config
control_config = {"temperature": 0.2, "seed": 13}

# Refined uses different config - DON'T DO THIS!
refined_config = {"temperature": 0.7, "seed": 42}
```

### ✅ **CORRECT: Complete data with same config**
```json
{
  "sample_idx": 0,
  "dataset": "truthfulqa",
  "framework": "praas",
  "original_prompt": "Why are bananas yellow?",
  "refined_prompt": "Why are bananas yellow in color?",
  "control_output": "Bananas are yellow because...",
  "refined_output": "Bananas are yellow due to...",
  "refinement_latency_ms": 4500.5,
  "refinement_tokens": {"input": 76, "output": 178, "total": 254},
  "control_generation_latency_ms": 1200.3,
  "control_generation_tokens": {"input": 10, "output": 150, "total": 160},
  "refined_generation_latency_ms": 1300.7,
  "refined_generation_tokens": {"input": 15, "output": 155, "total": 170},
  "total_latency_ms": 6001.5,
  "total_tokens": 584
}
```

---

## 🔍 GPT-5 Judge Input Format

Later, for each sample, we'll construct this prompt for GPT-5:

```
You are evaluating two LLM outputs for the following question:

QUESTION: {original_prompt}

OUTPUT A (Control): {control_output}

OUTPUT B (Refined): {refined_output}

Which output is better in terms of:
1. Accuracy/Correctness
2. Completeness
3. Clarity
4. Helpfulness

Provide:
- Winner: A or B or TIE
- Reasoning: Brief explanation
- Scores: Rate each output 1-10
```

**This is why we need both outputs!**

---

## 📊 Directory Structure

```
/home/comparison/
├── results_complete/
│   ├── control_truthfulqa_COMPLETE.json
│   ├── control_gsm8k_COMPLETE.json
│   ├── opro_truthfulqa_COMPLETE.json
│   ├── opro_gsm8k_COMPLETE.json
│   ├── promptagent_truthfulqa_COMPLETE.json
│   ├── promptwizard_gsm8k_COMPLETE.json
│   ├── ape_ambigqa_COMPLETE.json
│   └── ...
└── gpt5_evaluations/
    ├── control_vs_opro_truthfulqa.json
    ├── control_vs_praas_gsm8k.json
    └── ...
```

---

## 🎯 Summary for jw1

**To ensure compatibility, your PRaaS framework evaluation must:**

1. **Save files named:** `praas_{dataset}_COMPLETE.json`
2. **Include all required fields** (especially `control_output` and `refined_output`)
3. **Use same LLM config:** Llama-3.2-3B, temp=0.2, top_p=0.9, seed=13
4. **Generate both outputs:**
   - Control: Original prompt → LLM
   - Refined: Refined prompt → LLM
5. **Save as JSON array** with one object per sample
6. **Use exact field names** as specified above

---

## 📞 Questions?

If anything is unclear, refer to the smoke test output:
```
/home/comparison/smoke_test_results/COMPREHENSIVE_smoke_test.json
```

This file contains 60 real examples (20 test cases × 3 samples each) showing the exact format.

---

**Version Control:**
- v1.0 (2025-11-07): Initial specification
- Schema is now **LOCKED** - do not modify field names or structure

**Rules used:** [JW-Global, MPR-Detected: yes]

