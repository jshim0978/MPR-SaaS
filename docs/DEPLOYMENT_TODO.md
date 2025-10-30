# PRaaS/MPR-SaaS Deployment TODO List
## Training Server (sbs29) → Production Nodes Deployment

**Date:** 2025-10-31  
**Training Server (Current):** sbs29.etri.re.kr (129.254.184.194)  
**Target Nodes:** jw1 (251), jw2 (252), jw3 (253), kcloud (129)

---

## 🎯 MISSION OVERVIEW

### Mission 1: Git Repository Management
**Goal:** Commit and push all code (excluding large models/datasets) to git repository

### Mission 2: Model Distribution
**Goal:** Send trained LoRA adapters to corresponding production nodes

---

## 📋 DETAILED TODO LIST

### PHASE 1: Pre-flight Checks ✅
- [ ] 1.1 Verify all models are trained and ready
- [ ] 1.2 Check git repository status
- [ ] 1.3 Verify .gitignore is properly configured
- [ ] 1.4 Create model distribution manifest
- [ ] 1.5 Verify SSH connectivity to all nodes

### PHASE 2: Git Operations 📦
- [ ] 2.1 Stage all code/config files (respecting .gitignore)
- [ ] 2.2 Create comprehensive commit message
- [ ] 2.3 Verify what will be committed (dry run)
- [ ] 2.4 Execute git commit
- [ ] 2.5 Push to remote repository
- [ ] 2.6 Verify push success

### PHASE 3: Model Packaging 📁
- [ ] 3.1 Create model distribution directory structure
- [ ] 3.2 Package Cleaner models (3B + 8B)
  - [ ] llama32_3b_grammar_lora → for jw2
  - [ ] llama31_8b_grammar_lora → for jw2 (appendix)
- [ ] 3.3 Package Describer models (3B + 8B)
  - [ ] llama32_3b_wikipedia_only_lora → for jw3
  - [ ] llama31_8b_wikipedia_only_lora → for jw3 (appendix)
- [ ] 3.4 Package Paraphraser models (3B + 8B)
  - [ ] llama32_3b_paraphrase_lora → for kcloud
  - [ ] llama31_8b_paraphrase_lora → for kcloud (appendix)
- [ ] 3.5 Create SHA256 checksums for all models
- [ ] 3.6 Create deployment manifest with model metadata

### PHASE 4: Model Distribution 🚀
- [ ] 4.1 Transfer Cleaner models to jw2 (129.254.202.252)
  - [ ] Create target directory /home/models/ on jw2
  - [ ] SCP/rsync llama32_3b_grammar_lora
  - [ ] SCP/rsync llama31_8b_grammar_lora
  - [ ] Verify checksums on jw2
- [ ] 4.2 Transfer Describer models to jw3 (129.254.202.253)
  - [ ] Create target directory /home/models/ on jw3
  - [ ] SCP/rsync llama32_3b_wikipedia_only_lora
  - [ ] SCP/rsync llama31_8b_wikipedia_only_lora
  - [ ] Verify checksums on jw3
- [ ] 4.3 Transfer Paraphraser models to kcloud (129.254.202.129)
  - [ ] Create target directory /home/models/ on kcloud
  - [ ] SCP/rsync llama32_3b_paraphrase_lora
  - [ ] SCP/rsync llama31_8b_paraphrase_lora
  - [ ] Verify checksums on kcloud

### PHASE 5: Code Distribution 💻
- [ ] 5.1 Pull latest code on jw1 (master node)
  - [ ] SSH to jw1 and git pull
  - [ ] Verify code sync
- [ ] 5.2 Pull latest code on jw2 (cleaner)
  - [ ] SSH to jw2 and git pull
  - [ ] Verify code sync
- [ ] 5.3 Pull latest code on jw3 (describer)
  - [ ] SSH to jw3 and git pull
  - [ ] Verify code sync
- [ ] 5.4 Pull latest code on kcloud (paraphraser)
  - [ ] SSH to kcloud and git pull
  - [ ] Verify code sync

### PHASE 6: Verification & Documentation 📝
- [ ] 6.1 Test SSH connectivity to all nodes
- [ ] 6.2 Verify models are accessible on each node
- [ ] 6.3 Create deployment log
- [ ] 6.4 Update deployment manifest
- [ ] 6.5 Create smoke test checklist for each node
- [ ] 6.6 Document next steps for framework implementation

---

## 📊 MODEL DISTRIBUTION MATRIX

| Model Type | Size | Source Path | Destination | Target Node | IP |
|------------|------|-------------|-------------|-------------|-----|
| **Cleaner** | 3B | `llama32_3b_grammar_lora` | `/home/models/` | jw2 | 129.254.202.252 |
| **Cleaner** | 8B | `llama31_8b_grammar_lora` | `/home/models/` | jw2 | 129.254.202.252 |
| **Describer** | 3B | `llama32_3b_wikipedia_only_lora` | `/home/models/` | jw3 | 129.254.202.253 |
| **Describer** | 8B | `llama31_8b_wikipedia_only_lora` | `/home/models/` | jw3 | 129.254.202.253 |
| **Paraphraser** | 3B | `llama32_3b_paraphrase_lora` | `/home/models/` | kcloud | 129.254.202.129 |
| **Paraphraser** | 8B | `llama31_8b_paraphrase_lora` | `/home/models/` | kcloud | 129.254.202.129 |

---

## ⚠️ IMPORTANT NOTES

### What Gets Committed to Git:
✅ configs/, scripts/, docs/
✅ README.md, requirements.txt, .gitignore
✅ LLaMA-Factory/data/dataset_info.json
❌ models/ (too large - distribute separately)
❌ data/ (too large)
❌ logs/, hf_cache/

### Transfer Method:
- Use `rsync` for efficient transfer with progress and resume capability
- Verify SHA256 checksums after each transfer
- Keep deployment manifest for audit trail

### Security:
- Use SSH key authentication (no passwords in scripts)
- Verify fingerprints on first connection
- Log all transfer operations

---

## 🚀 EXECUTION ESTIMATE

- Phase 1: Pre-flight (5 min)
- Phase 2: Git ops (3 min)
- Phase 3: Packaging (10 min)
- Phase 4: Model distribution (30-60 min depending on network)
- Phase 5: Code distribution (5 min)
- Phase 6: Verification (10 min)

**Total: ~1-1.5 hours**

---

## 📋 SUCCESS CRITERIA

✅ All code committed and pushed to git
✅ All 6 models (3 roles × 2 sizes) transferred to correct nodes
✅ SHA256 checksums verified on all targets
✅ Code synced on all 4 production nodes
✅ Deployment manifest created and logged
✅ Ready for framework implementation (Week 1 plan)

---

**Status:** READY TO EXECUTE
**Next:** Begin Phase 1 - Pre-flight Checks

