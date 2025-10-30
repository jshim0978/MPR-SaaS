#!/bin/bash

set -x

# Set environment variables
export WANDB_API_KEY="24f409fbaaeba6cc7cfa494a259ef4d56664a7af"
export WANDB_PROJECT="knowledge-llama-enhancement"
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=1

echo "🚀 Starting Llama 3.2 3B Knowledge Enhancement Fine-tuning"
echo "=========================================="
echo "📊 W&B Project: knowledge-llama-enhancement"
echo "🔗 Dashboard: https://wandb.ai/jshim0978/knowledge-llama-enhancement"
echo "📁 Datasets: Wikidata + Wikipedia + KILT"
echo "🎯 Task: Knowledge-based Q&A"
echo "🎯 Method: LoRA (rank=16, alpha=32)"
echo "🖥️  Device: GPU cuda:0"
echo "=========================================="

# Change to LLaMA-Factory directory
cd /home/LLaMA-Factory

# Run training using LLaMA-Factory CLI
llamafactory-cli train /home/configs/knowledge/3b_knowledge.yaml 2>&1 | tee /home/llama32_3b_knowledge_training.log

echo ""
echo "=========================================="
echo "✅ Training completed!"
echo "📁 Model saved to: /home/models/llama32_3b_knowledge_lora"
echo "📊 Logs saved to: /home/llama32_3b_knowledge_training.log"
echo "=========================================="

