# Multi-Node Deployment Guide

## Quick Start

Run the automated script:
```bash
/home/scripts/deployment/git_commit_and_deploy.sh
```

Or follow the manual steps below.

---

## Manual Deployment Steps

### Step 1: Git Commit (Current Node)

```bash
cd /home

# Initialize git if not already done
git init

# Configure git user
git config user.email "jshim0978@gmail.com"
git config user.name "JW"

# Add remote (replace with your actual repo URL)
# git remote add origin <your-repo-url>

# Stage files (gitignore will filter automatically)
git add .

# Create commit
git commit -m "feat: complete LLaMA fine-tuning pipeline with dataset comparison

- Add grammar enhancement training (JFLEG dataset)
- Add paraphrase training (PAWS + QQP combined)
- Add knowledge enhancement training (Wikipedia + KILT)
- Add dataset comparison (PAWS-only vs QQP-only vs Combined)
- Implement optimized parallel training scheduler
- Create comprehensive evaluation scripts
- Organize repository with clean structure
- Document all training phases and deployment

Training completed:
- 7/10 models complete (grammar, paraphrase, knowledge)
- 3/10 models in progress (dataset comparison)"

# Push to remote
git push origin main  # or: git push origin master
```

---

### Step 2: Sync to Worker Nodes

#### For Each Node (jw1, jw2, jw3, kcloud@129.254.202.129):

```bash
# SSH into the node
ssh <node-name>  # e.g., ssh jw1, ssh jw2, ssh jw3, ssh kcloud@129.254.202.129

# Navigate to repository
cd /home  # or wherever the repo is located

# Stash any local changes (if any)
git stash

# Pull latest changes
git pull origin main  # or: git pull origin master

# Verify sync
git log -1

# Exit
exit
```

#### Automated Multi-Node Sync:

```bash
# From current node, sync all workers at once:
for NODE in jw1 jw2 jw3; do
    echo "Syncing $NODE..."
    ssh "$NODE" "cd /home && git pull origin main" || echo "Failed to sync $NODE"
done

# Sync kcloud
ssh kcloud@129.254.202.129 "cd /home && git pull origin main"
```

---

### Step 3: Verify Sync on Each Node

After syncing, verify on each node:

```bash
# Check git status
git status

# Check latest commit
git log -1 --oneline

# Verify directory structure
ls -la /home/

# Check if configs are present
ls -la /home/configs/

# Check if scripts are present
ls -la /home/scripts/
```

---

## What Gets Synced vs What Doesn't

### ✅ WILL BE SYNCED (via git):

```
/home/
├── .gitignore              ← Git rules
├── README.md               ← Documentation
├── QUICK_REFERENCE.txt     ← Quick reference
├── requirements.txt        ← Python dependencies
├── configs/                ← All training configs
├── scripts/                ← All scripts
├── docs/                   ← Documentation
└── LLaMA-Factory/data/dataset_info.json  ← Dataset registry
```

**Size**: ~500KB (very small, fast sync)

### ❌ WON'T BE SYNCED (local/manual transfer):

```
/home/
├── models/                 ← Model weights (~10-50GB)
├── data/                   ← Datasets (~300MB)
├── logs/                   ← Training logs (~25MB)
├── hf_cache/               ← HF cache (~20GB)
└── LLaMA-Factory/          ← Framework (~2GB)
```

These need to be:
- **LLaMA-Factory**: Installed separately on each node
- **hf_cache**: Downloaded on each node (or copied manually)
- **data/**: Generated using dataset prep scripts
- **models/**: Deployed separately (see below)
- **logs/**: Local artifacts, not needed on other nodes

---

## Step 4: Deploy Model Weights (After Training)

Model weights are NOT committed to git. Deploy them manually:

### Model Assignment Strategy:

**jw1 (Orchestrator)**:
- Needs access to ALL models for routing decisions
- Can use NFS/shared storage, or load specific models on demand

**jw2 (Cleaner)**:
- Primary: `llama32_3b_grammar_lora` (fast grammar correction)
- Backup: `llama31_8b_grammar_lora`

**jw3 (Describer)**:
- Primary: `llama31_8b_knowledge_lora` (high-quality descriptions)
- Secondary: `llama31_8b_paraphrase_lora`

### Deploy via rsync:

```bash
# From training node to jw2 (cleaner)
rsync -avz --progress \
  /home/models/llama32_3b_grammar_lora/ \
  jw2:/home/models/llama32_3b_grammar_lora/

# From training node to jw3 (describer)
rsync -avz --progress \
  /home/models/llama31_8b_knowledge_lora/ \
  jw3:/home/models/llama31_8b_knowledge_lora/

# For kcloud
rsync -avz --progress \
  /home/models/llama32_3b_grammar_lora/ \
  kcloud@129.254.202.129:/home/models/llama32_3b_grammar_lora/
```

### Or deploy via Hugging Face Hub:

```bash
# Upload to HF Hub (from training node)
huggingface-cli login
huggingface-cli upload your-username/llama32-3b-grammar-lora \
  /home/models/llama32_3b_grammar_lora/

# Download on worker nodes
huggingface-cli download your-username/llama32-3b-grammar-lora \
  --local-dir /home/models/llama32_3b_grammar_lora/
```

---

## Step 5: Post-Sync Setup on Worker Nodes

After syncing code, each worker node needs:

### 1. Install LLaMA-Factory (if not present):

```bash
cd /home
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e .
```

### 2. Install Python Dependencies:

```bash
cd /home
pip install -r requirements.txt
```

### 3. Set Environment Variables:

```bash
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"
```

### 4. Download Base Models (if needed):

```bash
# Will auto-download on first use, or manually:
python3 << EOF
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    cache_dir="/home/hf_cache"
)
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    cache_dir="/home/hf_cache"
)
EOF
```

### 5. Prepare Datasets (if needed):

```bash
cd /home
bash scripts/dataset_prep/run_all_paraphrase_prep.sh
bash scripts/dataset_prep/run_all_knowledge_prep.sh
```

---

## Verification Checklist

After deployment, verify on each node:

```bash
# ✅ Code synced
git status
git log -1 --oneline

# ✅ Configs present
ls /home/configs/

# ✅ Scripts present
ls /home/scripts/

# ✅ LLaMA-Factory installed
llamafactory-cli --version

# ✅ Python packages installed
pip list | grep transformers
pip list | grep peft

# ✅ Model weights present (if deployed)
ls /home/models/

# ✅ Environment variables set
echo $HF_HOME
echo $TRANSFORMERS_CACHE
```

---

## Node Status Summary

After deployment, each node should have:

### Current Training Node (you are here):
- ✅ Full repository with code/configs
- ✅ All 10 models (some training)
- ✅ All datasets
- ✅ Training logs
- ✅ Git initialized and committed

### jw1 (Orchestrator):
- ✅ Code synced via git
- ✅ LLaMA-Factory installed
- ⏳ Models: Deploy all or use on-demand loading
- 🎯 Role: Route requests, skip-gate, combiner

### jw2 (Cleaner):
- ✅ Code synced via git
- ✅ LLaMA-Factory installed
- ⏳ Models: `llama32_3b_grammar_lora` (primary)
- 🎯 Role: Minimal grammar/typo correction

### jw3 (Describer):
- ✅ Code synced via git
- ✅ LLaMA-Factory installed
- ⏳ Models: `llama31_8b_knowledge_lora` (primary)
- 🎯 Role: Task specification & entity extraction

### kcloud@129.254.202.129:
- ✅ Code synced via git
- ✅ LLaMA-Factory installed
- ⏳ Models: TBD based on usage
- 🎯 Role: TBD

---

## Quick Commands

```bash
# Commit current work
cd /home && git add . && git commit -m "your message" && git push

# Sync all nodes
for NODE in jw1 jw2 jw3; do ssh "$NODE" "cd /home && git pull"; done
ssh kcloud@129.254.202.129 "cd /home && git pull"

# Deploy model to specific node
rsync -avz /home/models/MODEL_NAME/ NODE:/home/models/MODEL_NAME/

# Verify node status
ssh NODE "cd /home && git status && ls models/"
```

---

## Troubleshooting

### Git conflicts on worker nodes:
```bash
git stash
git pull
# If needed: git stash pop
```

### SSH connection issues:
```bash
# Test connection
ssh -v NODE "echo 'Connection OK'"

# Check SSH keys
ls -la ~/.ssh/
```

### Model loading issues on worker nodes:
```bash
# Check CUDA
nvidia-smi

# Check Python packages
pip list | grep -E "transformers|peft|torch"

# Test model loading
python3 -c "from transformers import AutoModelForCausalLM; print('OK')"
```

---

## Summary

1. **Commit**: `git add . && git commit && git push`
2. **Sync**: SSH to each node and `git pull`
3. **Deploy**: Use `rsync` or HF Hub for model weights
4. **Verify**: Check git status, configs, scripts, models
5. **Done**: All nodes synced and ready!

For automated deployment, use: `/home/scripts/deployment/git_commit_and_deploy.sh`

