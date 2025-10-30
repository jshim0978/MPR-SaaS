# Post-Training Deployment Plan

## Overview
After all dataset comparison training completes (~14 hours), we need to:
1. Commit and push all changes to git
2. Sync worker nodes with the updated repository
3. Deploy fine-tuned model weights to corresponding servers

---

## Phase 1: Git Commit & Push

### What to Commit
- ✅ All training scripts (`scripts/training/`)
- ✅ All configuration files (`configs/`)
- ✅ Dataset preparation scripts
- ✅ Evaluation scripts (`scripts/evaluation/`)
- ✅ Documentation (`docs/`, `README.md`, `QUICK_REFERENCE.txt`)
- ❌ **Exclude**: Model weights (too large for git)
- ❌ **Exclude**: Training logs (local artifacts)
- ❌ **Exclude**: HF cache

### Git Operations
```bash
# 1. Review changes
git status
git diff

# 2. Add relevant files
git add configs/
git add scripts/
git add docs/
git add README.md
git add QUICK_REFERENCE.txt
git add LLaMA-Factory/data/dataset_info.json

# 3. Commit with descriptive message
git commit -m "feat: complete dataset comparison training for paraphrase justification

- Add PAWS-only and QQP-only training configs for 3B and 8B models
- Implement optimized parallel training scheduler
- Create evaluation scripts for model comparison
- Reorganize repository structure for clarity
- Document all training phases and results"

# 4. Push to remote
git push origin main
```

---

## Phase 2: Sync Worker Nodes

### Worker Node Sync Strategy
Assuming you have multiple worker nodes that need the updated code:

```bash
# On each worker node:
ssh worker-node-1 << 'EOF'
  cd /path/to/repo
  git fetch origin
  git pull origin main
  # Verify sync
  git log -1
EOF

# Repeat for worker-node-2, worker-node-3, etc.
```

### What Gets Synced
- Training scripts (consistent execution across nodes)
- Configuration files (same hyperparameters)
- Dataset preparation logic (reproducibility)
- Evaluation scripts (unified assessment)

---

## Phase 3: Deploy Model Weights

### Model Inventory
After training completes, you'll have these models:

**Grammar Enhancement (JFLEG)**
- `/home/models/llama32_3b_grammar_lora/`
- `/home/models/llama31_8b_grammar_lora/`

**Paraphrase (Combined)**
- `/home/models/llama32_3b_paraphrase_lora/`
- `/home/models/llama31_8b_paraphrase_lora/`

**Paraphrase (PAWS-only)**
- `/home/models/llama32_3b_paws_only_lora/`
- `/home/models/llama31_8b_paws_only_lora/`

**Paraphrase (QQP-only)**
- `/home/models/llama32_3b_qqp_only_lora/`
- `/home/models/llama31_8b_qqp_only_lora/`

**Knowledge Enhancement**
- `/home/models/llama32_3b_knowledge_lora/`
- `/home/models/llama31_8b_knowledge_lora/`

**Total: 10 fine-tuned models**

### Deployment Options

#### Option A: Direct Copy (Fast, for local network)
```bash
# Copy to server via rsync
rsync -avz --progress \
  /home/models/llama32_3b_grammar_lora/ \
  user@server1:/models/llama32_3b_grammar_lora/

rsync -avz --progress \
  /home/models/llama31_8b_grammar_lora/ \
  user@server2:/models/llama31_8b_grammar_lora/
```

#### Option B: Upload to Hugging Face Hub (Recommended for distribution)
```bash
# Install/upgrade huggingface_hub
pip install -U huggingface_hub

# Login (one-time)
huggingface-cli login

# Upload each model
huggingface-cli upload your-username/llama32-3b-grammar-lora \
  /home/models/llama32_3b_grammar_lora/
```

#### Option C: Shared Storage (For multi-node clusters)
```bash
# Copy to NFS/shared storage
cp -r /home/models/* /shared/storage/models/

# Worker nodes can access from:
# /shared/storage/models/llama32_3b_grammar_lora/
```

### Server Assignment Strategy

**Recommendation based on model size and use case:**

**Server 1 (Cleaner/Grammar - Low latency required)**
- `llama32_3b_grammar_lora` ← Fastest inference
- `llama32_3b_paraphrase_lora` ← Production model

**Server 2 (Describer/Knowledge - Quality over speed)**
- `llama31_8b_knowledge_lora` ← Best quality
- `llama31_8b_grammar_lora` ← Backup/comparison

**Server 3 (Comparison/Research)**
- All PAWS-only and QQP-only models
- For A/B testing and research

---

## Phase 4: Verification

### Post-Deployment Checks
1. **Model Loading Test**: Verify each model loads on target server
2. **Inference Test**: Run sample prompts through each deployed model
3. **Performance Benchmark**: Measure latency and throughput
4. **Git Sync Verification**: Confirm all worker nodes on same commit

### Verification Script Template
```bash
# On each server after deployment
python3 << 'EOF'
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Test loading
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    device_map="auto"
)
model = PeftModel.from_pretrained(base_model, "/path/to/deployed/model")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")

# Test inference
prompt = "Fix this grammar: He go to school yesterday."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0]))
EOF
```

---

## Automation Script Location

All deployment automation scripts will be in:
- `/home/scripts/deployment/`
  - `prepare_git_commit.sh` - Prepare and commit changes
  - `sync_workers.sh` - Sync all worker nodes
  - `deploy_models.sh` - Deploy model weights
  - `verify_deployment.sh` - Post-deployment verification

---

## Timeline

**Current**: Training in progress (~14h remaining)
**After training**:
1. Git commit & push: ~10 minutes
2. Worker sync: ~5 minutes per node
3. Model deployment: ~30-60 minutes per model (depends on transfer method)
4. Verification: ~20 minutes

**Total deployment time**: ~2-3 hours for all 10 models

---

## Notes

- **Model Size**: Each LoRA adapter is ~20-100 MB (much smaller than full model)
- **Base Models**: Worker nodes should already have base Llama models cached
- **Credentials**: Ensure SSH keys and HF tokens are configured before deployment
- **Backup**: Keep local copies until deployment is verified

---

## MPR-Agents Integration

If this is for MPR-Agents (detected based on your rules):
- **jw1 (Orchestrator)**: Needs access to all models for routing decisions
- **jw2 (Cleaner)**: Deploy `llama32_3b_grammar_lora` (faster, adequate quality)
- **jw3 (Describer)**: Deploy `llama31_8b_knowledge_lora` (higher quality needed)

The paraphrase models can be used for prompt variation in the orchestrator.

