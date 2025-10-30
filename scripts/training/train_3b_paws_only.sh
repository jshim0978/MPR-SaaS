#!/bin/bash

set -x

# Set environment variables
export WANDB_API_KEY="24f409fbaaeba6cc7cfa494a259ef4d56664a7af"
export WANDB_PROJECT="knowledge-dataset-comparison"
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=0

echo "🚀 Starting Llama 3.2 3B PAWS-Only Fine-tuning"
echo "=========================================="
echo "📊 W&B Project: paraphrase-dataset-comparison"
echo "📁 Dataset: PAWS only (43,658 examples)"
echo "🎯 Method: LoRA (rank=16, alpha=32)"
echo "🖥️  Device: GPU cuda:0"
echo "=========================================="

cd /home/LLaMA-Factory

llamafactory-cli train /home/configs/dataset_comparison/3b_paws_only.yaml 2>&1 | tee /home/llama32_3b_paws_only_training.log

echo ""
echo "=========================================="
echo "✅ Training completed!"
echo "📁 Model saved to: /home/models/llama32_3b_paws_only_lora"
echo "=========================================="

