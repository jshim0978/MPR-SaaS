#!/bin/bash

# Set environment variables
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=0

echo "🔍 Comparing Original vs Fine-tuned Models"
echo "============================================================"
echo ""
echo "This will evaluate 20 samples from JFLEG test set"
echo "Comparing 4 models:"
echo "  1. Llama 3.2 3B Original"
echo "  2. Llama 3.2 3B Fine-tuned"
echo "  3. Llama 3.1 8B Original"
echo "  4. Llama 3.1 8B Fine-tuned"
echo ""
echo "⏱️  This will take approximately 5-10 minutes..."
echo "============================================================"
echo ""

python3 /home/compare_original_vs_finetuned.py

