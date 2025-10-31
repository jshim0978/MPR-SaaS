# PRaaS/MPR-SaaS Multi-Node Deployment Instructions

**Date:** October 31, 2025  
**Training Server:** sbs29 (root@129.254.202.29)  
**Repository:** https://github.com/jshim0978/MPR-SaaS  

---

## 📋 Overview

This guide provides step-by-step instructions for deploying the PRaaS/MPR-SaaS system across 4 nodes:

- **jw1** (129.254.202.251) - Orchestrator (router, arbiter, merger, fallback)
- **jw2** (129.254.202.252) - Cleaner worker (grammar/typo fixes)
- **jw3** (129.254.202.253) - Describer worker (Wikipedia knowledge expansion)
- **kcloud** (129.254.202.129) - Backup/testing node

---

## 🚀 STEP 1: Deploy from Training Server (sbs29)

**You are here** → Execute these commands on **sbs29** (training server)

### 1.1 Sync Code to All Nodes

```bash
# On sbs29 (training server)
cd /home
/home/scripts/deployment/git_sync_nodes.sh
```

This will:
- SSH to each node (jw1, jw2, jw3, kcloud)
- Clone/pull latest code from GitHub
- Install dependencies from `requirements.txt`
- Verify deployment

### 1.2 Distribute Trained Models

```bash
# On sbs29 (training server)
cd /home
/home/scripts/deployment/distribute_models.sh
```

This will transfer:
- **jw2:** Grammar Cleaner models (3B + 8B LoRA adapters)
- **jw3:** Wikipedia Describer models (3B + 8B LoRA adapters)
- **kcloud:** Wiki+Wikidata backup models (3B + 8B LoRA adapters)

**Estimated time:** 30-60 minutes depending on network speed

---

## 🖥️ STEP 2: Per-Node Setup

After Step 1 completes, follow these instructions **on each specific node**:

---

## NODE: jw2 (Cleaner Worker)

**IP:** 129.254.202.252  
**User:** etri  
**Role:** Grammar correction and typo fixing  
**Models:** 3B + 8B Grammar LoRA adapters  

### SSH to jw2

```bash
ssh etri@129.254.202.252
```

### Verify Deployment

```bash
cd /home
ls -la

# Expected structure:
# /home/
#   ├── mpr/
#   ├── workers/cleaner/
#   ├── config/
#   ├── prompts/
#   └── models/
#       ├── llama32_3b_grammar_lora/
#       └── llama31_8b_grammar_lora/
```

### Verify Models

```bash
ls -lh /home/models/llama32_3b_grammar_lora/
ls -lh /home/models/llama31_8b_grammar_lora/

# Should see:
#   - adapter_config.json
#   - adapter_model.safetensors
#   - tokenizer files
```

### Download Base Models (if not cached)

```bash
# Ensure HuggingFace cache has base models
cd /home

# For 3B model
python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
model_id = "meta-llama/Llama-3.2-3B-Instruct"
print(f"Downloading {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir="/home/hf_cache")
print("✅ 3B model cached")
EOF

# For 8B model
python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
model_id = "meta-llama/Llama-3.1-8B-Instruct"
print(f"Downloading {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir="/home/hf_cache")
print("✅ 8B model cached")
EOF
```

### Test Cleaner Worker

```bash
cd /home/workers/cleaner

# Test model loading
python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base_model_id = "meta-llama/Llama-3.2-3B-Instruct"
lora_path = "/home/models/llama32_3b_grammar_lora"

print("Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id, cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained(base_model_id, cache_dir="/home/hf_cache")

print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(model, lora_path)

print("✅ Cleaner model loaded successfully!")
EOF
```

### Start Cleaner Service (when ready)

```bash
cd /home/workers/cleaner
python3 app.py

# Expected output:
# 🧹 Cleaner Worker Starting...
# 📦 Model: Llama-3.2-3B-Instruct + Grammar LoRA
# 🌐 Listening on: 0.0.0.0:8002
```

**Keep this terminal open** or run in `tmux`/`screen`

---

## NODE: jw3 (Describer Worker)

**IP:** 129.254.202.253  
**User:** etri  
**Role:** Knowledge expansion with Wikipedia training  
**Models:** 3B + 8B Wikipedia-only LoRA adapters  

### SSH to jw3

```bash
ssh etri@129.254.202.253
```

### Verify Deployment

```bash
cd /home
ls -la

# Expected structure:
# /home/
#   ├── mpr/
#   ├── workers/descr/
#   ├── config/
#   ├── prompts/
#   └── models/
#       ├── llama32_3b_wikipedia_only_lora/
#       └── llama31_8b_wikipedia_only_lora/
```

### Verify Models

```bash
ls -lh /home/models/llama32_3b_wikipedia_only_lora/
ls -lh /home/models/llama31_8b_wikipedia_only_lora/

# Should see LoRA adapter files
```

### Download Base Models

```bash
# Same as jw2 - download 3B and 8B base models
cd /home

python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM

for model_id in ["meta-llama/Llama-3.2-3B-Instruct", "meta-llama/Llama-3.1-8B-Instruct"]:
    print(f"Downloading {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir="/home/hf_cache")
    model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir="/home/hf_cache")
    print(f"✅ {model_id} cached")
EOF
```

### Test Describer Worker

```bash
cd /home/workers/descr

python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base_model_id = "meta-llama/Llama-3.2-3B-Instruct"
lora_path = "/home/models/llama32_3b_wikipedia_only_lora"

print("Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id, cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained(base_model_id, cache_dir="/home/hf_cache")

print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(model, lora_path)

print("✅ Describer model loaded successfully!")
print(f"Model quality: 8.8/10 (from evaluation)")
EOF
```

### Start Describer Service (when ready)

```bash
cd /home/workers/descr
python3 app.py

# Expected output:
# 📝 Describer Worker Starting...
# 📦 Model: Llama-3.2-3B-Instruct + Wikipedia LoRA
# 🌐 Listening on: 0.0.0.0:8003
```

---

## NODE: jw1 (Orchestrator)

**IP:** 129.254.202.251  
**User:** etri  
**Role:** Router, Arbiter, Merger, Fallback logic  
**Models:** None (calls jw2 and jw3 via HTTP)  

### SSH to jw1

```bash
ssh etri@129.254.202.251
```

### Verify Deployment

```bash
cd /home
ls -la

# Expected structure:
# /home/
#   ├── mpr/
#   ├── orchestrator/
#   ├── config/
#   └── prompts/
```

### Configure Worker Endpoints

```bash
cd /home/config

# Check decoding.json exists
cat decoding.json

# Expected: {"temperature": 0.7, "max_new_tokens": 512, ...}
```

### Update Orchestrator Config (if needed)

```bash
# Edit orchestrator/app.py to point to correct worker IPs
cd /home/orchestrator

# Verify worker endpoints in code:
grep -n "CLEANER_URL\|DESCRIBER_URL" app.py

# Should see:
# CLEANER_URL = "http://129.254.202.252:8002"
# DESCRIBER_URL = "http://129.254.202.253:8003"
```

### Test Orchestrator (after jw2/jw3 are running)

```bash
cd /home/orchestrator

# Test health check
python3 << 'EOF'
import requests

cleaner = requests.get("http://129.254.202.252:8002/health")
describer = requests.get("http://129.254.202.253:8003/health")

print(f"Cleaner: {cleaner.json()}")
print(f"Describer: {describer.json()}")
EOF
```

### Start Orchestrator (when workers ready)

```bash
cd /home/orchestrator
python3 app.py

# Expected output:
# 🎯 Orchestrator Starting...
# 🔗 Cleaner:   http://129.254.202.252:8002
# 🔗 Describer: http://129.254.202.253:8003
# 🌐 Listening on: 0.0.0.0:8000
```

---

## NODE: kcloud (Backup/Testing)

**IP:** 129.254.202.129  
**User:** root  
**Role:** Backup models and testing  
**Models:** 3B + 8B Wiki+Wikidata LoRA adapters  

### SSH to kcloud

```bash
ssh root@129.254.202.129
```

### Verify Deployment

```bash
cd /home
ls -la

# Expected:
# /home/
#   ├── mpr/
#   ├── workers/
#   ├── config/
#   └── models/
#       ├── llama32_3b_knowledge_wiki_only_lora/
#       └── llama31_8b_knowledge_wiki_only_lora/
```

### Verify Models

```bash
ls -lh /home/models/llama32_3b_knowledge_wiki_only_lora/
ls -lh /home/models/llama31_8b_knowledge_wiki_only_lora/
```

### Download Base Models

```bash
# Same process as jw2/jw3
cd /home

python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM

for model_id in ["meta-llama/Llama-3.2-3B-Instruct", "meta-llama/Llama-3.1-8B-Instruct"]:
    print(f"Downloading {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir="/home/hf_cache")
    model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir="/home/hf_cache")
    print(f"✅ {model_id} cached")
EOF
```

### Test Backup Models

```bash
cd /home

python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base_model_id = "meta-llama/Llama-3.2-3B-Instruct"
lora_path = "/home/models/llama32_3b_knowledge_wiki_only_lora"

print("Loading Wiki+Wikidata backup model...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id, cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained(base_model_id, cache_dir="/home/hf_cache")
model = PeftModel.from_pretrained(model, lora_path)

print("✅ Backup model loaded successfully!")
print("Quality: 8.2/10 (balanced, good for testing)")
EOF
```

---

## 🔍 STEP 3: End-to-End Verification

After all nodes are running, test the full pipeline from **jw1**:

```bash
# On jw1 (orchestrator)
cd /home

# Test full pipeline
python3 << 'EOF'
import requests
import json

orchestrator_url = "http://localhost:8000/refine"

# Test prompt
payload = {
    "prompt": "what is the captial of frane?",  # Intentional typo
    "run_id": "test-001",
    "idempotency_key": "test-001"
}

print("Sending test prompt to orchestrator...")
response = requests.post(orchestrator_url, json=payload)
result = response.json()

print("\n" + "="*60)
print("ORIGINAL PROMPT:", payload["prompt"])
print("="*60)
print("\n📝 REFINED PROMPT:")
print(result.get("refined_prompt"))
print("\n🔧 CLEANER OUTPUT:")
print(result.get("cleaner_output"))
print("\n📚 DESCRIBER OUTPUT:")
print(result.get("describer_output"))
print("\n⏱️  LATENCY:", result.get("latency_ms"), "ms")
print("="*60)
EOF
```

Expected behavior:
- **Cleaner** fixes typo: "frane" → "France"
- **Describer** adds context: "France is a country in Western Europe..."
- **Merger** combines: Clean + informative final prompt

---

## 📊 STEP 4: Monitoring & Verification

### Check Logs on Each Node

```bash
# On each node (jw1, jw2, jw3)
tail -f /home/logs/*.log
```

### Health Checks

```bash
# From any node
curl http://129.254.202.251:8000/health  # Orchestrator
curl http://129.254.202.252:8002/health  # Cleaner
curl http://129.254.202.253:8003/health  # Describer
```

### Monitor Resources

```bash
# GPU usage
nvidia-smi

# Memory
free -h

# Disk space
df -h /home
```

---

## 🐛 Troubleshooting

### Issue: SSH connection refused
**Solution:** Verify SSH service is running and firewall allows connections

```bash
sudo systemctl status sshd
sudo firewall-cmd --list-all
```

### Issue: Model not found
**Solution:** Re-run model distribution from sbs29

```bash
# On sbs29
/home/scripts/deployment/distribute_models.sh
```

### Issue: Import errors (missing dependencies)
**Solution:** Install requirements

```bash
cd /home
pip3 install -r requirements.txt
```

### Issue: CUDA out of memory
**Solution:** Use smaller model (3B instead of 8B) or reduce batch size

```bash
# Edit config/decoding.json
nano /home/config/decoding.json
# Reduce max_new_tokens or use 3B model
```

### Issue: Worker not responding
**Solution:** Check if process is running and restart

```bash
# Find process
ps aux | grep app.py

# Kill if needed
pkill -f "python3 app.py"

# Restart
cd /home/workers/cleaner  # or /descr or /orchestrator
python3 app.py
```

---

## 📝 Quick Reference: Node Roles

| Node | IP | Role | Models | Service Port |
|------|-----|------|--------|--------------|
| jw1 | 129.254.202.251 | Orchestrator | None | 8000 |
| jw2 | 129.254.202.252 | Cleaner | Grammar 3B+8B | 8002 |
| jw3 | 129.254.202.253 | Describer | Wikipedia 3B+8B | 8003 |
| kcloud | 129.254.202.129 | Backup | Wiki+Wikidata 3B+8B | N/A |

---

## 🎯 Success Criteria

✅ All nodes have latest code from GitHub  
✅ All models transferred and verified  
✅ Base models cached on worker nodes  
✅ Worker services running and responding  
✅ Orchestrator can reach both workers  
✅ End-to-end test returns refined prompt  
✅ Logs show successful requests  

---

## 📞 Next Steps After Deployment

1. **Run HHEM Benchmark** - Test hallucination reduction
2. **Measure Latency** - p50/p95 metrics
3. **Implement Arbiter** - Skip-gate for clean prompts
4. **Add Merger Logic** - Intent-preserving combination
5. **Add Fallback** - Timeout/error handling
6. **Enable Telemetry** - Prometheus metrics

See `/home/.cursor/rules/eacl-manuscript-rules.mdc` for full architecture details.

---

**Rules used:** [JW-Global, MPR-Detected]

