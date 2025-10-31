# COMPLETE DEPLOYMENT GUIDE - Copy-Paste Scripts for All Nodes

**Date**: October 31, 2025  
**Architecture**: 3-Worker System (Cleaner + Describer + Paraphraser)  

---

## 🚀 Quick Start

Each node has a **single self-contained script** that handles everything:
- SSH key generation and setup
- Git clone (no credentials needed - public repo)
- Python dependencies installation
- Model transfer from sbs29
- HuggingFace model downloads
- Testing and verification

---

## 📋 Prerequisites

### On Training Server (sbs29):
Nothing! Just wait for worker nodes to show their SSH public keys.

### On Each Worker Node:
- Internet access (for GitHub and HuggingFace)
- Network access to sbs29 (129.254.202.29)
- Python 3.8+
- Basic tools (git, rsync, ssh)

---

## 🎯 Deployment Order

### 1. JW1 (Orchestrator) - EASIEST
**No SSH or model transfers needed!**

```bash
ssh etri@129.254.202.251
# Copy entire content of COPY_PASTE_JW1.sh and paste
bash
```

### 2. JW2 (Cleaner Worker)
```bash
ssh etri@129.254.202.252
# Copy entire content of COPY_PASTE_JW2.sh and paste
bash
```

**During execution:**
1. Script generates SSH key
2. **PAUSE**: Shows public key → Add to sbs29's `~/.ssh/authorized_keys`
3. Press Enter to continue
4. Script transfers models and sets up everything

### 3. JW3 (Describer Worker)
```bash
ssh etri@129.254.202.253
# Copy entire content of COPY_PASTE_JW3.sh and paste
bash
```

**Same process**: Generate key → Add to sbs29 → Continue

### 4. KCLOUD (Paraphraser Worker)
```bash
ssh root@129.254.202.129
# Copy entire content of COPY_PASTE_KCLOUD.sh and paste
bash
```

**Same process**: Generate key → Add to sbs29 → Continue

---

## 🔑 SSH Key Setup (For JW2, JW3, KCLOUD)

Each worker script will:
1. Generate SSH key automatically
2. Display the public key
3. Wait for you to add it to sbs29

### Adding Keys to SBS29

On **sbs29 (training server)**, run:

```bash
# For jw2:
echo 'ssh-ed25519 AAAA... jw2-cleaner' >> ~/.ssh/authorized_keys

# For jw3:
echo 'ssh-ed25519 AAAA... jw3-describer' >> ~/.ssh/authorized_keys

# For kcloud:
echo 'ssh-ed25519 AAAA... kcloud-paraphraser' >> ~/.ssh/authorized_keys

# Set permissions:
chmod 600 ~/.ssh/authorized_keys
```

Each script will show you the exact key to copy!

---

## 🤗 HuggingFace Authentication

All worker nodes need to download Meta Llama models from HuggingFace.

### First Time Setup (on each worker):

```bash
# Install HuggingFace CLI
pip3 install --upgrade huggingface_hub

# Login with your token
huggingface-cli login
# Paste your token when prompted

# Accept Llama license:
# Visit: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
# Click "Access repository" and accept terms
```

### Get Your Token:
1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Give it "Read" access
4. Copy the token

**Note**: The scripts will prompt you if authentication fails!

---

## ⏱️ Timeline

| Step | Time | Notes |
|------|------|-------|
| **JW1 Setup** | 5 min | No models needed |
| **JW2 Setup** | 45-60 min | Grammar models (~500MB) + base models (~7GB) |
| **JW3 Setup** | 45-60 min | Wikipedia models (~500MB) + base models (~7GB) |
| **KCLOUD Setup** | 45-60 min | Paraphrase models (~500MB) + base models (~7GB) |

**Total**: ~2-3 hours (can run JW2, JW3, KCLOUD in parallel)

---

## ✅ Verification Checklist

After each script completes:

### JW1 (Orchestrator)
```bash
ls -la /home/orchestrator/app.py  # ✓ Code exists
pip3 list | grep fastapi           # ✓ Dependencies installed
```

### JW2 (Cleaner)
```bash
ls -la /home/models/llama32_3b_grammar_lora/  # ✓ LoRA adapter
ls -la /home/hf_cache/                         # ✓ Base models
python3 -c "from peft import PeftModel"        # ✓ PEFT works
```

### JW3 (Describer)
```bash
ls -la /home/models/llama32_3b_wikipedia_only_lora/  # ✓ LoRA adapter
ls -la /home/hf_cache/                                # ✓ Base models
```

### KCLOUD (Paraphraser)
```bash
ls -la /home/models/llama32_3b_paraphrase_lora/  # ✓ LoRA adapter
ls -la /home/hf_cache/                            # ✓ Base models
```

---

## 🚦 Starting Services

**Start workers first, orchestrator last!**

### 1. Start Workers (any order, can be parallel):

```bash
# On jw2:
cd /home/workers/cleaner
python3 app.py &

# On jw3:
cd /home/workers/descr
python3 app.py &

# On kcloud:
cd /home/workers/paraphraser
python3 app.py &
```

### 2. Wait for workers to be ready (check health):

```bash
curl http://129.254.202.252:8002/health  # jw2
curl http://129.254.202.253:8003/health  # jw3
curl http://129.254.202.129:8004/health  # kcloud
```

### 3. Start Orchestrator (on jw1):

```bash
cd /home/orchestrator
python3 app.py
```

---

## 🧪 End-to-End Test

After all services are running:

```bash
# Health check:
curl http://129.254.202.251:8000/health

# Full pipeline test:
curl -X POST http://129.254.202.251:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what is the captial of frane?"}'
```

**Expected**: Cleaned, described, and paraphrased output!

---

## 🐛 Troubleshooting

### "Permission denied (publickey)"
- **Issue**: SSH key not added to sbs29
- **Fix**: Copy public key to sbs29's `~/.ssh/authorized_keys`

### "401 Unauthorized" (HuggingFace)
- **Issue**: No HF authentication or no Llama license
- **Fix**: 
  1. `huggingface-cli login`
  2. Accept license at https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct

### "No module named 'transformers'"
- **Issue**: Dependencies not installed
- **Fix**: `pip3 install -r requirements.txt --user`

### "rsync: Connection refused"
- **Issue**: Can't reach sbs29
- **Fix**: Check network connectivity: `ping 129.254.202.29`

### "Port already in use"
- **Issue**: Service already running
- **Fix**: `pkill -f "python3 app.py"` then restart

---

## 📁 Script Locations

All copy-paste scripts are in:
```
/home/
├── COPY_PASTE_JW1.sh      ← JW1 (Orchestrator)
├── COPY_PASTE_JW2.sh      ← JW2 (Cleaner)
├── COPY_PASTE_JW3.sh      ← JW3 (Describer)
└── COPY_PASTE_KCLOUD.sh   ← KCLOUD (Paraphraser)
```

---

## 🎯 What Each Script Does

### All Scripts:
1. ✅ Check/install prerequisites (git, pip)
2. ✅ Clone code from GitHub (no auth needed)
3. ✅ Install Python dependencies
4. ✅ Test final setup

### Worker Scripts (JW2, JW3, KCLOUD):
5. ✅ Generate SSH key
6. ⏸️  **Wait for you to add key to sbs29**
7. ✅ Transfer LoRA models from sbs29
8. ✅ Download base Llama models from HuggingFace
9. ✅ Test model loading

---

## 🔒 Security Notes

- SSH keys are generated per-node (not shared)
- GitHub repo is public (no credentials needed)
- HuggingFace requires your personal token (keep it secret!)
- Models transferred over SSH (encrypted)

---

## 📞 Need Help?

If scripts fail, check:
1. Network connectivity to sbs29 and internet
2. SSH keys properly added to sbs29
3. HuggingFace authentication completed
4. Sufficient disk space (~10GB per worker)

---

**Status**: ✅ Ready for copy-paste deployment!  
**Repository**: https://github.com/jshim0978/MPR-SaaS  
**Last Updated**: October 31, 2025

