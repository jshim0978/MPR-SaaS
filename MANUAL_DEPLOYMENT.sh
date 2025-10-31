#!/bin/bash
# Manual Deployment Guide - Run Commands on Each Node
# Since SSH key setup from sbs29 is not available, we'll do manual deployment

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║          MANUAL DEPLOYMENT: Pull Code on Each Node                        ║
╚═══════════════════════════════════════════════════════════════════════════╝

📦 Repository: https://github.com/jshim0978/MPR-SaaS
🔑 You have direct access to each node, so pull code directly!

═══════════════════════════════════════════════════════════════════════════
STEP 1: Deploy Code to Each Node
═══════════════════════════════════════════════════════════════════════════

On EACH node (jw1, jw2, jw3, kcloud), run these commands:

ssh <user>@<node>

# Then on the node:
cd /home

# If /home doesn't have git repo yet:
git clone https://github.com/jshim0978/MPR-SaaS.git temp
rsync -av temp/ ./
rm -rf temp

# OR if /home already has .git:
git pull origin main

# Install dependencies:
pip3 install -r requirements.txt --user

# Verify:
ls -la /home
# Should see: mpr/, orchestrator/, workers/, config/, prompts/

═══════════════════════════════════════════════════════════════════════════
STEP 2: Transfer Models from sbs29
═══════════════════════════════════════════════════════════════════════════

Since we can't SSH from sbs29 → nodes, we'll do the reverse:
Pull models FROM sbs29 TO each node.

───────────────────────────────────────────────────────────────────────────
ON jw2 (Cleaner Worker) - ssh etri@129.254.202.252
───────────────────────────────────────────────────────────────────────────

mkdir -p /home/models

# Pull Grammar models from sbs29:
rsync -avz --progress root@129.254.202.29:/home/models/llama32_3b_grammar_lora/ \
    /home/models/llama32_3b_grammar_lora/

rsync -avz --progress root@129.254.202.29:/home/models/llama31_8b_grammar_lora/ \
    /home/models/llama31_8b_grammar_lora/

# Verify:
ls -lh /home/models/

───────────────────────────────────────────────────────────────────────────
ON jw3 (Describer Worker) - ssh etri@129.254.202.253
───────────────────────────────────────────────────────────────────────────

mkdir -p /home/models

# Pull Wikipedia models from sbs29:
rsync -avz --progress root@129.254.202.29:/home/models/llama32_3b_wikipedia_only_lora/ \
    /home/models/llama32_3b_wikipedia_only_lora/

rsync -avz --progress root@129.254.202.29:/home/models/llama31_8b_wikipedia_only_lora/ \
    /home/models/llama31_8b_wikipedia_only_lora/

# Verify:
ls -lh /home/models/

───────────────────────────────────────────────────────────────────────────
ON jw1 (Orchestrator) - ssh etri@129.254.202.251
───────────────────────────────────────────────────────────────────────────

# No models needed! Just code (already pulled in Step 1)

# Verify code:
ls -la /home/orchestrator/
ls -la /home/mpr/

───────────────────────────────────────────────────────────────────────────
ON kcloud (Backup) - ssh root@129.254.202.129
───────────────────────────────────────────────────────────────────────────

mkdir -p /home/models

# Pull Wiki+Wikidata models from sbs29:
rsync -avz --progress root@129.254.202.29:/home/models/llama32_3b_knowledge_wiki_only_lora/ \
    /home/models/llama32_3b_knowledge_wiki_only_lora/

rsync -avz --progress root@129.254.202.29:/home/models/llama31_8b_knowledge_wiki_only_lora/ \
    /home/models/llama31_8b_knowledge_wiki_only_lora/

# Verify:
ls -lh /home/models/

═══════════════════════════════════════════════════════════════════════════
STEP 3: Download Base Models on Worker Nodes
═══════════════════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────────────────────
ON jw2 and jw3 (worker nodes that need base models):
───────────────────────────────────────────────────────────────────────────

cd /home

python3 << 'PYEOF'
from transformers import AutoTokenizer, AutoModelForCausalLM

# Download 3B model
print("Downloading Llama-3.2-3B-Instruct...")
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    cache_dir="/home/hf_cache"
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    cache_dir="/home/hf_cache"
)
print("✅ 3B model cached")

# Download 8B model
print("Downloading Llama-3.1-8B-Instruct...")
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    cache_dir="/home/hf_cache"
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    cache_dir="/home/hf_cache"
)
print("✅ 8B model cached")
PYEOF

═══════════════════════════════════════════════════════════════════════════
STEP 4: Test Model Loading
═══════════════════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────────────────────
ON jw2 (test Grammar Cleaner):
───────────────────────────────────────────────────────────────────────────

cd /home

python3 << 'PYEOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base_model_id = "meta-llama/Llama-3.2-3B-Instruct"
lora_path = "/home/models/llama32_3b_grammar_lora"

print("Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id, cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained(base_model_id, cache_dir="/home/hf_cache")

print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(model, lora_path)

print("✅ jw2 Cleaner model loaded successfully!")
PYEOF

───────────────────────────────────────────────────────────────────────────
ON jw3 (test Wikipedia Describer):
───────────────────────────────────────────────────────────────────────────

cd /home

python3 << 'PYEOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base_model_id = "meta-llama/Llama-3.2-3B-Instruct"
lora_path = "/home/models/llama32_3b_wikipedia_only_lora"

print("Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id, cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained(base_model_id, cache_dir="/home/hf_cache")

print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(model, lora_path)

print("✅ jw3 Describer model loaded successfully!")
print("Model quality: 8.8/10 (from evaluation)")
PYEOF

═══════════════════════════════════════════════════════════════════════════
STEP 5: Start Services
═══════════════════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────────────────────
ON jw2 (Cleaner Worker):
───────────────────────────────────────────────────────────────────────────

cd /home/workers/cleaner
python3 app.py

# Expected output:
# 🧹 Cleaner Worker Starting...
# 📦 Model: Llama-3.2-3B-Instruct + Grammar LoRA
# 🌐 Listening on: 0.0.0.0:8002

───────────────────────────────────────────────────────────────────────────
ON jw3 (Describer Worker):
───────────────────────────────────────────────────────────────────────────

cd /home/workers/descr
python3 app.py

# Expected output:
# 📝 Describer Worker Starting...
# 📦 Model: Llama-3.2-3B-Instruct + Wikipedia LoRA
# 🌐 Listening on: 0.0.0.0:8003

───────────────────────────────────────────────────────────────────────────
ON jw1 (Orchestrator) - START LAST, after jw2 and jw3 are running:
───────────────────────────────────────────────────────────────────────────

cd /home/orchestrator
python3 app.py

# Expected output:
# 🎯 Orchestrator Starting...
# 🔗 Cleaner:   http://129.254.202.252:8002
# 🔗 Describer: http://129.254.202.253:8003
# 🌐 Listening on: 0.0.0.0:8000

═══════════════════════════════════════════════════════════════════════════
STEP 6: Verify End-to-End
═══════════════════════════════════════════════════════════════════════════

From jw1 (or any node):

# Health checks:
curl http://129.254.202.252:8002/health
curl http://129.254.202.253:8003/health
curl http://129.254.202.251:8000/health

# Full test:
curl -X POST http://129.254.202.251:8000/refine \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "what is the captial of frane?",
    "run_id": "test-001",
    "idempotency_key": "test-001"
  }'

# Expected:
# - Cleaner fixes: "frane" → "France"
# - Describer adds: "France is a country in Western Europe..."
# - Merger combines both

═══════════════════════════════════════════════════════════════════════════
📋 QUICK REFERENCE
═══════════════════════════════════════════════════════════════════════════

Node  | IP              | User | Clone Code | Pull Models From sbs29
------|-----------------|------|------------|------------------------
jw1   | 129.254.202.251 | etri | ✅         | ❌ (no models needed)
jw2   | 129.254.202.252 | etri | ✅         | Grammar 3B + 8B
jw3   | 129.254.202.253 | etri | ✅         | Wikipedia 3B + 8B
kcloud| 129.254.202.129 | root | ✅         | Wiki+Wikidata 3B + 8B

═══════════════════════════════════════════════════════════════════════════
⏱️  TIMELINE
═══════════════════════════════════════════════════════════════════════════

Step 1 (Code pull):           5 min per node  = 20 min total (parallel)
Step 2 (Model transfer):     30-40 min per node = 40 min (parallel)
Step 3 (Base model download): 20-30 min per node = 30 min (parallel)
Step 4 (Test):                5 min per node  = 10 min
Step 5 (Start services):      5 min
Step 6 (Verify):              5 min

Total: ~2 hours (mostly waiting for downloads)

EOF

