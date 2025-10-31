#!/bin/bash
# JW2 DEPLOYMENT SCRIPT - Cleaner Worker
# IP: 129.254.202.252
# User: etri
# Role: Grammar correction and typo fixing

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║                    JW2: CLEANER WORKER DEPLOYMENT                         ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF

# Step 1: Clone code
echo "📥 STEP 1: Pulling code from GitHub..."
cd /home
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/jshim0978/MPR-SaaS.git temp
    rsync -av temp/ ./
    rm -rf temp
fi

# Step 2: Install dependencies
echo "📦 STEP 2: Installing dependencies..."
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt --user
fi

# Step 3: Transfer models from sbs29
echo "📦 STEP 3: Transferring Grammar models from sbs29..."
mkdir -p /home/models

echo "  → Transferring 3B Grammar model..."
rsync -avz --progress root@129.254.202.29:/home/models/llama32_3b_grammar_lora/ \
    /home/models/llama32_3b_grammar_lora/

echo "  → Transferring 8B Grammar model..."
rsync -avz --progress root@129.254.202.29:/home/models/llama31_8b_grammar_lora/ \
    /home/models/llama31_8b_grammar_lora/

# Step 4: Download base models
echo "📥 STEP 4: Downloading base models from HuggingFace..."
python3 << 'PYEOF'
from transformers import AutoTokenizer, AutoModelForCausalLM

# Download 3B model
print("Downloading Llama-3.2-3B-Instruct...")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", cache_dir="/home/hf_cache")
print("✅ 3B model cached")

# Download 8B model
print("Downloading Llama-3.1-8B-Instruct...")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", cache_dir="/home/hf_cache")
print("✅ 8B model cached")
PYEOF

# Step 5: Test model loading
echo "🧪 STEP 5: Testing model loading..."
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

cat << 'EOF'

═══════════════════════════════════════════════════════════════════════════
✅ JW2 SETUP COMPLETE!
═══════════════════════════════════════════════════════════════════════════

🚀 TO START SERVICE:
   cd /home/workers/cleaner
   python3 app.py

Expected output:
  🧹 Cleaner Worker Starting...
  📦 Model: Llama-3.2-3B-Instruct + Grammar LoRA
  🌐 Listening on: 0.0.0.0:8002

🔍 TO TEST:
   curl http://localhost:8002/health

EOF

