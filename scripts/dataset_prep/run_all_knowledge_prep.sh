#!/bin/bash

set -e

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  Knowledge Dataset Preparation Pipeline                               ║"
echo "║  Datasets: Wikidata + Wikipedia + KILT                                ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Set environment
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"

echo "📦 Step 1/2: Preparing knowledge datasets..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 /home/scripts/dataset_prep/prep_knowledge.py
echo ""

echo "📦 Step 2/2: Updating LLaMA-Factory dataset_info.json..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Copy to LLaMA-Factory
cp /home/data/knowledge_combined.json /home/LLaMA-Factory/data/

# Update dataset_info.json
python3 << 'EOF'
import json

# Load existing dataset_info.json
with open("/home/LLaMA-Factory/data/dataset_info.json", "r") as f:
    dataset_info = json.load(f)

# Add knowledge_combined dataset
dataset_info["knowledge_combined"] = {
    "file_name": "knowledge_combined.json",
    "formatting": "sharegpt",
    "columns": {
        "messages": "messages"
    },
    "tags": {
        "role_tag": "role",
        "content_tag": "content",
        "user_tag": "user",
        "assistant_tag": "assistant",
        "system_tag": "system"
    }
}

# Save updated dataset_info.json
with open("/home/LLaMA-Factory/data/dataset_info.json", "w") as f:
    json.dump(dataset_info, f, indent=2)

print("✅ Updated dataset_info.json")
EOF

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Knowledge datasets prepared successfully!                          ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Output files:"
echo "   • /home/data/wikidata_knowledge.jsonl"
echo "   • /home/data/wikipedia_knowledge.jsonl"
echo "   • /home/data/kilt_wow_knowledge.jsonl"
echo "   • /home/data/knowledge_combined_train.jsonl"
echo "   • /home/data/knowledge_combined.json (LLaMA-Factory format)"
echo ""
echo "🎯 Ready for fine-tuning!"
echo "   Config files: /home/llama32_3b_knowledge_config.yaml"
echo "                 /home/llama31_8b_knowledge_config.yaml"

