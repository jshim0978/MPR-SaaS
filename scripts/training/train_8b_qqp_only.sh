#!/bin/bash

set -x

export WANDB_API_KEY="${WANDB_API_KEY:-your_wandb_key_here}"
export WANDB_PROJECT="knowledge-dataset-comparison"
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=0

echo "🚀 Starting Llama 3.1 8B QQP-Only Fine-tuning"
echo "=========================================="
echo "📊 W&B Project: paraphrase-dataset-comparison"
echo "📁 Dataset: QQP only (100,000 examples)"
echo "🎯 Method: LoRA (rank=16, alpha=32)"
echo "🖥️  Device: GPU cuda:0"
echo "=========================================="

cd /home/LLaMA-Factory

llamafactory-cli train /home/configs/dataset_comparison/8b_qqp_only.yaml 2>&1 | tee /home/llama31_8b_qqp_only_training.log

echo ""
echo "=========================================="
echo "✅ Training completed!"
echo "📁 Model saved to: /home/models/llama31_8b_qqp_only_lora"
echo "=========================================="

