#!/bin/bash
# COMPLETE KCLOUD SETUP - Copy and paste this entire script
# Includes: SSH key setup, Git clone, HuggingFace access, model transfer

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║              KCLOUD: PARAPHRASER WORKER COMPLETE SETUP                    ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF

set -e

# Configuration
SBS29_IP="129.254.202.29"
SBS29_USER="root"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 1: Setup SSH access to sbs29 (training server)"
echo "═══════════════════════════════════════════════════════════════════════════"

# Generate SSH key if not exists
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "kcloud-paraphraser"
    echo "✅ SSH key generated"
fi

# Display public key for manual addition to sbs29
echo ""
echo "📋 YOUR SSH PUBLIC KEY (add this to sbs29's ~/.ssh/authorized_keys):"
echo "════════════════════════════════════════════════════════════════════════"
cat ~/.ssh/id_ed25519.pub
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  ACTION REQUIRED:"
echo "   1. Copy the key above"
echo "   2. On sbs29, run: echo '<YOUR_KEY>' >> ~/.ssh/authorized_keys"
echo "   3. Press Enter here when done..."
read -p ""

# Test SSH connection
echo "Testing SSH connection to sbs29..."
if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 ${SBS29_USER}@${SBS29_IP} "echo OK" &>/dev/null; then
    echo "✅ SSH connection successful"
else
    echo "❌ SSH connection failed. Please check:"
    echo "   - Is the public key added to sbs29?"
    echo "   - Can you reach sbs29 from this node?"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 2: Clone code from GitHub"
echo "═══════════════════════════════════════════════════════════════════════════"

cd /home

# Install git if needed
if ! command -v git &> /dev/null; then
    echo "Installing git..."
    sudo yum install -y git || sudo apt-get install -y git
fi

# Clone repository (public, no auth needed)
if [ -d ".git" ]; then
    echo "Repository exists, pulling latest..."
    git pull origin main || git fetch origin && git reset --hard origin/main
else
    echo "Cloning repository..."
    git clone https://github.com/jshim0978/MPR-SaaS.git temp
    rsync -av temp/ ./
    rm -rf temp
    cd /home
fi

echo "✅ Code cloned"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 3: Install Python dependencies"
echo "═══════════════════════════════════════════════════════════════════════════"

# Install pip if needed
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    sudo yum install -y python3-pip || sudo apt-get install -y python3-pip
fi

# Install dependencies
if [ -f requirements.txt ]; then
    echo "Installing Python packages..."
    pip3 install -r requirements.txt --user
fi

echo "✅ Dependencies installed"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 4: Transfer Paraphrase models from sbs29"
echo "═══════════════════════════════════════════════════════════════════════════"

mkdir -p /home/models

echo "Transferring 3B Paraphrase model (this may take 10-15 minutes)..."
rsync -avz --progress ${SBS29_USER}@${SBS29_IP}:/home/models/llama32_3b_paraphrase_lora/ \
    /home/models/llama32_3b_paraphrase_lora/

echo ""
echo "Transferring 8B Paraphrase model (this may take 15-20 minutes)..."
rsync -avz --progress ${SBS29_USER}@${SBS29_IP}:/home/models/llama31_8b_paraphrase_lora/ \
    /home/models/llama31_8b_paraphrase_lora/

echo "✅ Models transferred (Training: PAWS + QQP, 143,658 samples)"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 5: Download base models from HuggingFace"
echo "═══════════════════════════════════════════════════════════════════════════"

echo "⚠️  NOTE: This requires HuggingFace access to Meta Llama models"
echo "   If you get authentication errors:"
echo "   1. Visit: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct"
echo "   2. Accept the license agreement"
echo "   3. Get your HF token: https://huggingface.co/settings/tokens"
echo "   4. Login: huggingface-cli login"
echo ""
echo "Press Enter to continue (or Ctrl+C to setup HF auth first)..."
read -p ""

python3 << 'PYEOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

os.environ['HF_HOME'] = '/home/hf_cache'
os.environ['TRANSFORMERS_CACHE'] = '/home/hf_cache'

try:
    # Download 3B model
    print("Downloading Llama-3.2-3B-Instruct (this may take 10-20 minutes)...")
    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Llama-3.2-3B-Instruct",
        cache_dir="/home/hf_cache",
        token=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-3.2-3B-Instruct",
        cache_dir="/home/hf_cache",
        token=True
    )
    print("✅ 3B model cached")
    
    # Download 8B model
    print("\nDownloading Llama-3.1-8B-Instruct (this may take 20-30 minutes)...")
    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Llama-3.1-8B-Instruct",
        cache_dir="/home/hf_cache",
        token=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-3.1-8B-Instruct",
        cache_dir="/home/hf_cache",
        token=True
    )
    print("✅ 8B model cached")
    
except Exception as e:
    print(f"❌ Error downloading models: {e}")
    print("\nTo fix authentication:")
    print("  1. pip install --upgrade huggingface_hub")
    print("  2. huggingface-cli login")
    print("  3. Paste your HF token")
    print("  4. Re-run this script")
    exit 1
PYEOF

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "STEP 6: Test model loading"
echo "═══════════════════════════════════════════════════════════════════════════"

python3 << 'PYEOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base_model_id = "meta-llama/Llama-3.2-3B-Instruct"
lora_path = "/home/models/llama32_3b_paraphrase_lora"

print("Testing model loading...")
print("  Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id, cache_dir="/home/hf_cache")
model = AutoModelForCausalLM.from_pretrained(base_model_id, cache_dir="/home/hf_cache")

print("  Loading LoRA adapter...")
model = PeftModel.from_pretrained(model, lora_path)

print("✅ kcloud Paraphraser model loaded successfully!")
print("   Training: PAWS + QQP (143,658 paraphrase pairs)")
PYEOF

cat << 'COMPLETE'

═══════════════════════════════════════════════════════════════════════════
✅ KCLOUD SETUP COMPLETE!
═══════════════════════════════════════════════════════════════════════════

📋 Status:
  ✓ SSH access to sbs29 configured
  ✓ Code cloned from GitHub
  ✓ Dependencies installed
  ✓ Paraphrase models transferred (3B + 8B, 143K samples)
  ✓ Base models downloaded from HuggingFace
  ✓ Model loading tested

🚀 TO START SERVICE:

   cd /home/workers/paraphraser
   python3 app.py

Expected output:
  🔄 Paraphraser Worker Starting...
  📦 Model: Llama-3.2-3B-Instruct + Paraphrase LoRA
  🌐 Listening on: 0.0.0.0:8004

🧪 TO TEST:
   curl http://localhost:8004/health

COMPLETE

echo ""
echo "✅ All done! KCLOUD is ready to start service."

