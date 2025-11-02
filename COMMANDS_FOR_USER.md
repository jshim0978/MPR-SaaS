# Simple Deployment Commands - Just Provide SSH Keys

Run these commands on each node. When asked, paste the SSH keys I provide.

---

## 🔑 SSH Key Generation (I'll Do This)

I'll generate keys and provide them to you. You just paste when prompted.

---

## 📋 Commands for Each Node

### JW1 (Orchestrator) - `ssh etri@129.254.202.251`

```bash
cd /home && \
git clone https://github.com/jshim0978/MPR-SaaS.git temp && \
rsync -av temp/ ./ && rm -rf temp && \
pip3 install -r requirements.txt --user && \
echo "✅ JW1 Ready! Start: cd /home/orchestrator && python3 app.py"
```

---

### JW2 (Cleaner) - `ssh etri@129.254.202.252`

```bash
# Setup SSH key (I'll provide both private and public keys)
mkdir -p ~/.ssh && chmod 700 ~/.ssh

# Paste PRIVATE key (I'll give you this)
echo "Paste SSH private key, then press Ctrl+D:"
cat > ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519

# Paste PUBLIC key (I'll give you this)  
echo "Paste SSH public key, then press Ctrl+D:"
cat > ~/.ssh/id_ed25519.pub
chmod 644 ~/.ssh/id_ed25519.pub

# Test SSH
ssh -o StrictHostKeyChecking=no root@129.254.202.29 "echo OK"

# Clone and setup
cd /home && \
git clone https://github.com/jshim0978/MPR-SaaS.git temp && \
rsync -av temp/ ./ && rm -rf temp && \
pip3 install -r requirements.txt --user

# Transfer models
mkdir -p /home/models && \
rsync -avz --progress root@129.254.202.29:/home/models/llama32_3b_grammar_lora/ /home/models/llama32_3b_grammar_lora/ && \
rsync -avz --progress root@129.254.202.29:/home/models/llama31_8b_grammar_lora/ /home/models/llama31_8b_grammar_lora/

# Download base models (requires HF login first: huggingface-cli login)
python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
os.environ['HF_HOME'] = '/home/hf_cache'
print("Downloading 3B model...")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", cache_dir="/home/hf_cache", token=True)
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", cache_dir="/home/hf_cache", token=True)
print("Downloading 8B model...")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", cache_dir="/home/hf_cache", token=True)
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", cache_dir="/home/hf_cache", token=True)
print("✅ Done")
EOF

echo "✅ JW2 Ready! Start: cd /home/workers/cleaner && python3 app.py"
```

---

### JW3 (Describer) - `ssh etri@129.254.202.253`

```bash
# Setup SSH key (I'll provide both keys)
mkdir -p ~/.ssh && chmod 700 ~/.ssh

echo "Paste SSH private key, then press Ctrl+D:"
cat > ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519

echo "Paste SSH public key, then press Ctrl+D:"
cat > ~/.ssh/id_ed25519.pub
chmod 644 ~/.ssh/id_ed25519.pub

# Test SSH
ssh -o StrictHostKeyChecking=no root@129.254.202.29 "echo OK"

# Clone and setup
cd /home && \
git clone https://github.com/jshim0978/MPR-SaaS.git temp && \
rsync -av temp/ ./ && rm -rf temp && \
pip3 install -r requirements.txt --user

# Transfer models
mkdir -p /home/models && \
rsync -avz --progress root@129.254.202.29:/home/models/llama32_3b_wikipedia_only_lora/ /home/models/llama32_3b_wikipedia_only_lora/ && \
rsync -avz --progress root@129.254.202.29:/home/models/llama31_8b_wikipedia_only_lora/ /home/models/llama31_8b_wikipedia_only_lora/

# Download base models
python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
os.environ['HF_HOME'] = '/home/hf_cache'
print("Downloading 3B model...")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", cache_dir="/home/hf_cache", token=True)
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", cache_dir="/home/hf_cache", token=True)
print("Downloading 8B model...")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", cache_dir="/home/hf_cache", token=True)
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", cache_dir="/home/hf_cache", token=True)
print("✅ Done")
EOF

echo "✅ JW3 Ready! Start: cd /home/workers/descr && python3 app.py"
```

---

### KCLOUD (Paraphraser) - `ssh root@129.254.202.129`

```bash
# Setup SSH key (I'll provide both keys)
mkdir -p ~/.ssh && chmod 700 ~/.ssh

echo "Paste SSH private key, then press Ctrl+D:"
cat > ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519

echo "Paste SSH public key, then press Ctrl+D:"
cat > ~/.ssh/id_ed25519.pub
chmod 644 ~/.ssh/id_ed25519.pub

# Test SSH
ssh -o StrictHostKeyChecking=no root@129.254.202.29 "echo OK"

# Clone and setup
cd /home && \
git clone https://github.com/jshim0978/MPR-SaaS.git temp && \
rsync -av temp/ ./ && rm -rf temp && \
pip3 install -r requirements.txt --user

# Transfer models
mkdir -p /home/models && \
rsync -avz --progress root@129.254.202.29:/home/models/llama32_3b_paraphrase_lora/ /home/models/llama32_3b_paraphrase_lora/ && \
rsync -avz --progress root@129.254.202.29:/home/models/llama31_8b_paraphrase_lora/ /home/models/llama31_8b_paraphrase_lora/

# Download base models
python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
os.environ['HF_HOME'] = '/home/hf_cache'
print("Downloading 3B model...")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", cache_dir="/home/hf_cache", token=True)
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", cache_dir="/home/hf_cache", token=True)
print("Downloading 8B model...")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", cache_dir="/home/hf_cache", token=True)
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", cache_dir="/home/hf_cache", token=True)
print("✅ Done")
EOF

echo "✅ KCLOUD Ready! Start: cd /home/workers/paraphraser && python3 app.py"
```

---

## 🔐 Before Running Worker Commands

On each worker (jw2, jw3, kcloud), you need:

1. **HuggingFace authentication** (for downloading base models):
   ```bash
   pip3 install --upgrade huggingface_hub
   huggingface-cli login
   # Paste your HF token
   ```

2. **SSH keys** that I'll provide:
   - When script says "Paste SSH private key", paste the private key I give you
   - Press `Ctrl+D` after pasting
   - When it says "Paste SSH public key", paste the public key I give you
   - Press `Ctrl+D` after pasting

---

## 📝 Summary

**JW1**: No SSH keys needed (just git clone)
**JW2, JW3, KCLOUD**: You'll paste SSH keys when prompted

Let me know when you're ready and I'll generate the SSH keys for you!

