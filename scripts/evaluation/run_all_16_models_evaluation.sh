#!/bin/bash

# Run comprehensive evaluation of all 16 models

# Add all NVIDIA library paths
NVIDIA_LIBS="/usr/local/lib/python3.12/site-packages/nvidia/cusparselt/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvshmem/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvjitlink/lib:/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufile/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvtx/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparse/lib:/usr/local/lib/python3.12/site-packages/nvidia/curand/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufft/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusolver/lib"
export LD_LIBRARY_PATH=$NVIDIA_LIBS:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export HF_HOME=/home/hf_cache
export TRANSFORMERS_CACHE=/home/hf_cache
export WANDB_DISABLED=true
export CUDA_VISIBLE_DEVICES=0

LOG_FILE="/home/logs/evaluation_all_16_models.log"

echo "╔═══════════════════════════════════════════════════════════════════════════╗" | tee "$LOG_FILE"
echo "║           COMPREHENSIVE EVALUATION - ALL 16 MODELS                       ║" | tee -a "$LOG_FILE"
echo "╚═══════════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Started at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

python3 /home/scripts/evaluation/evaluate_all_16_models.py 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "Completed at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "✅ Evaluation complete! Results saved to:" | tee -a "$LOG_FILE"
echo "   /home/evaluation_results_all_16_models.json" | tee -a "$LOG_FILE"

