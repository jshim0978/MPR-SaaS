#!/bin/bash

# Paraphrase Dataset Comparison Evaluation
# Compares Original vs PAWS-only vs QQP-only vs Combined models

# Add all NVIDIA library paths
NVIDIA_LIBS="/usr/local/lib/python3.12/site-packages/nvidia/cusparselt/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvshmem/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvjitlink/lib:/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufile/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvtx/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparse/lib:/usr/local/lib/python3.12/site-packages/nvidia/curand/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufft/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusolver/lib"
export LD_LIBRARY_PATH=$NVIDIA_LIBS:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export HF_HOME=/home/hf_cache
export TRANSFORMERS_CACHE=/home/hf_cache
export WANDB_DISABLED=true

LOG_FILE="/home/logs/paraphrase_dataset_comparison.log"

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║     PARAPHRASE DATASET COMPARISON EVALUATION                              ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Comparing 8 models:"
echo "  3B: Original, PAWS-only, QQP-only, Combined"
echo "  8B: Original, PAWS-only, QQP-only, Combined"
echo ""
echo "Test samples: 20 per model"
echo "Estimated time: ~45-60 minutes"
echo ""
echo "Log: $LOG_FILE"
echo ""

cd /home
python3 scripts/evaluation/evaluate_paraphrase_datasets.py 2>&1 | tee "$LOG_FILE"

echo ""
echo "✅ Evaluation complete!"
echo "Results: /home/evaluation_results_paraphrase_dataset_comparison.json"

