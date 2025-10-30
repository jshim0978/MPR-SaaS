#!/bin/bash

set -x

# Set environment variables
export WANDB_API_KEY="24f409fbaaeba6cc7cfa494a259ef4d56664a7af"
export WANDB_PROJECT="paraphrase-llama-comparison"
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=1

echo "🚀 Starting Llama 3.1 8B Paraphrasing Fine-tuning"
echo "=========================================="
echo "📊 W&B Project: paraphrase-llama-comparison"
echo "🔗 Dashboard: https://wandb.ai/jshim0978/paraphrase-llama-comparison"
echo "📁 Dataset: PAWS + QQP (143,658 training examples)"
echo "🎯 Task: Bidirectional Paraphrase Generation"
echo "🎯 Method: LoRA (rank=16, alpha=32)"
echo "🖥️  Device: GPU cuda:1"
echo "=========================================="

# Change to LLaMA-Factory directory
cd /home/LLaMA-Factory

# Run training using LLaMA-Factory CLI
llamafactory-cli train /home/configs/paraphrase/8b_paraphrase_combined.yaml 2>&1 | tee /home/llama31_8b_paraphrase_training.log

echo ""
echo "=========================================="
echo "✅ Training completed!"
echo "📁 Model saved to: /home/models/llama31_8b_paraphrase_lora"
echo "📊 Logs saved to: /home/llama31_8b_paraphrase_training.log"
echo "=========================================="

