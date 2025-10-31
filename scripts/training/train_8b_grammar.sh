#!/bin/bash

# Set environment variables
export WANDB_API_KEY="${WANDB_API_KEY:-your_wandb_key_here}"
export WANDB_PROJECT="jfleg-llama-lora-comparison"
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=0

echo "🚀 Starting Llama 3.1 8B LoRA Fine-tuning"
echo "=========================================="
echo "📊 W&B Project: jfleg-llama-lora-comparison"
echo "🔗 Dashboard: https://wandb.ai/jshim0978/jfleg-llama-lora-comparison"
echo "📁 Dataset: JFLEG (4,809 training examples with all corrections)"
echo "🎯 Method: LoRA (rank=16, alpha=32)"
echo "🖥️  Device: GPU cuda:0"
echo "=========================================="

# Change to LLaMA-Factory directory
cd /home/LLaMA-Factory

# Run training using LLaMA-Factory CLI
llamafactory-cli train /home/configs/grammar/8b_grammar_jfleg.yaml 2>&1 | tee /home/llama31_8b_lora_training.log

echo ""
echo "=========================================="
echo "✅ Training completed!"
echo "📁 Model saved to: /home/models/llama31_8b_lora_factory"
echo "📊 Logs saved to: /home/llama31_8b_lora_training.log"
echo "=========================================="
