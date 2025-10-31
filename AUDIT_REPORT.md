# Repository Audit: Issues Found and Fixes Needed

**Date**: October 31, 2025  
**Audit Scope**: All configuration files, scripts, and documentation  

---

## 🔍 Issues Found

### 1. ❌ **Orchestrator Port Numbers Incorrect**
**File**: `/home/orchestrator/app.py`
**Lines**: 6-7
**Current**:
```python
CLEANER_URL = os.environ.get("CLEANER_URL", "http://129.254.202.252:9001")
DESCR_URL   = os.environ.get("DESCR_URL",   "http://129.254.202.253:9002")
```
**Problem**: Wrong ports! Workers use 8002 and 8003, not 9001/9002
**Should be**:
```python
CLEANER_URL = os.environ.get("CLEANER_URL", "http://129.254.202.252:8002")
DESCR_URL   = os.environ.get("DESCR_URL",   "http://129.254.202.253:8003")
```

### 2. ❌ **Orchestrator Endpoint Mismatch**
**File**: `/home/orchestrator/app.py`
**Line**: 40
**Current**: `call_json(f"{DESCR_URL}/descr", ...)`
**Problem**: Worker endpoint is `/describe` not `/descr`
**Should be**: `call_json(f"{DESCR_URL}/describe", ...)`

### 3. ❌ **Git Sync Script - Wrong Node Descriptions**
**File**: `/home/scripts/deployment/git_sync_nodes.sh`
**Lines**: 12-16
**Current**:
```
→ jw1 (129.254.202.251): Master/Gateway + Arbiter + Merger
→ jw2 (129.254.202.252): Cleaner Service
→ jw3 (129.254.202.253): Describer Service
→ kcloud (129.254.202.129): Paraphraser + Fallback
```
**Problem**: kcloud is NOT "Paraphraser" - it's backup/testing with Wiki+Wikidata models
**Should be**:
```
→ jw1 (129.254.202.251): Orchestrator
→ jw2 (129.254.202.252): Cleaner (Grammar)
→ jw3 (129.254.202.253): Describer (Wikipedia)
→ kcloud (129.254.202.129): Backup/Testing (Wiki+Wikidata)
```

### 4. ⚠️ **Git Sync Script - Placeholder URL**
**File**: `/home/scripts/deployment/git_sync_nodes.sh`
**Line**: 35
**Current**: `REPO_URL="YOUR_GIT_REPO_URL_HERE"`
**Should be**: `REPO_URL="https://github.com/jshim0978/MPR-SaaS.git"`

### 5. ⚠️ **Config Files Reference "knowledge_combined"**
**Files**: 
- `/home/configs/knowledge/3b_knowledge.yaml`
- `/home/configs/knowledge/8b_knowledge.yaml`

**Line**: 15
**Current**: `dataset: knowledge_combined`
**Problem**: "knowledge_combined" includes Wikipedia + Wikidata + KILT WOW (all 3)
**Reality**: 
- These models (`llama32_3b_knowledge_lora`, `llama31_8b_knowledge_lora`) were trained on all 3 sources
- But we selected Wikipedia-only and Wiki+Wikidata (NO KILT) for production
- These config files are just reference - models already trained

**Note**: These are reference configs. The actual deployed models are:
- `llama32_3b_wikipedia_only_lora` (Wikipedia only)
- `llama32_3b_knowledge_wiki_only_lora` (Wiki+Wikidata, no KILT)

### 6. ✅ **MANUAL_DEPLOYMENT.sh** - CORRECT
- Properly references Wikipedia-only models for jw3
- Correctly states Wiki+Wikidata for kcloud backup

### 7. ✅ **README.md** - CORRECT (just updated)
- Accurate training data descriptions
- Correct model selection rationale
- Properly excludes KILT from production

### 8. ✅ **distribute_models.sh** - CORRECT
- Correct model names for distribution
- Accurate Wikipedia-only for jw3

---

## 📋 Summary of Required Fixes

### Critical (Breaks Functionality)
1. Fix orchestrator worker URLs (ports 9001/9002 → 8002/8003)
2. Fix orchestrator endpoint (`/descr` → `/describe`)

### Important (Documentation Accuracy)
3. Update git_sync_nodes.sh node descriptions
4. Update git_sync_nodes.sh repo URL

### Informational (Already Correct in Practice)
5. Config files reference "knowledge_combined" but actual deployed models are correct

---

## 🎯 Dataset Reality Check

### What "knowledge_combined" Actually Contains:
According to `/home/scripts/dataset_prep/prep_knowledge.py`:
- Wikipedia: ~15-20K examples (encyclopedic articles)
- Wikidata: ~10K examples (entity descriptions)
- KILT WOW: ~10K examples (conversational dialogues)
- **Total: ~35-40K examples**

### What We Trained:
1. **llama32_3b_knowledge_lora / llama31_8b_knowledge_lora**:
   - Used `knowledge_combined` dataset
   - Contains all 3 sources (Wiki + Wikidata + KILT)
   - Trained but NOT selected for production

2. **llama32_3b_wikipedia_only_lora / llama31_8b_wikipedia_only_lora**:
   - Wikipedia only (14,982 samples)
   - Quality: 8.8/10
   - **SELECTED for jw3 production**

3. **llama32_3b_knowledge_wiki_only_lora / llama31_8b_knowledge_wiki_only_lora**:
   - Wikipedia (14,982) + Wikidata (10,000) = 24,982 samples
   - NO KILT WOW
   - Quality: 8.2-8.5/10
   - **SELECTED for kcloud backup**

### Evaluation Finding:
- KILT WOW caused conversational tone (unwanted)
- Wikipedia-only produced best detailed, encyclopedic responses
- Wiki+Wikidata offered good balance for backup

---

## ✅ Files That Are Already Correct

- README.md (just updated)
- MANUAL_DEPLOYMENT.sh
- docs/FINAL_MODEL_SELECTION.md
- scripts/deployment/distribute_models.sh
- workers/cleaner/app.py (except orchestrator calling it)
- workers/descr/app.py (except orchestrator calling it)
- requirements.txt
- prompts/*.md
- config/decoding.json

---

## 🔧 Next Actions

1. Fix orchestrator/app.py (worker URLs and endpoints)
2. Update git_sync_nodes.sh (descriptions and repo URL)
3. Optionally: Add comments to config files clarifying "knowledge_combined" vs production models

