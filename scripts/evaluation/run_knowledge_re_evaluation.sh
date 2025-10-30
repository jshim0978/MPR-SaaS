#!/bin/bash

# Re-evaluate knowledge models with improved system prompts

# Add all NVIDIA library paths
NVIDIA_LIBS="/usr/local/lib/python3.12/site-packages/nvidia/cusparselt/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvshmem/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvjitlink/lib:/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufile/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvtx/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparse/lib:/usr/local/lib/python3.12/site-packages/nvidia/curand/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufft/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusolver/lib"
export LD_LIBRARY_PATH=$NVIDIA_LIBS:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export HF_HOME=/home/hf_cache
export TRANSFORMERS_CACHE=/home/hf_cache
export WANDB_DISABLED=true

LOG_FILE="/home/logs/knowledge_re_evaluation.log"
mkdir -p /home/logs/

echo "╔═══════════════════════════════════════════════════════════════════════════╗" | tee "$LOG_FILE"
echo "║         RE-EVALUATING KNOWLEDGE MODELS WITH SYSTEM PROMPTS               ║" | tee -a "$LOG_FILE"
echo "╚═══════════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Started at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "This will re-evaluate all 10 knowledge models (3B and 8B) with an improved" | tee -a "$LOG_FILE"
echo "system prompt that guides them to generate informative descriptions." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

python3 /home/scripts/evaluation/re_evaluate_knowledge_models.py 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "╔═══════════════════════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║                     RE-EVALUATION COMPLETE!                               ║" | tee -a "$LOG_FILE"
echo "╚═══════════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "Results file: /home/evaluation_results_knowledge_with_system_prompt.json" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

