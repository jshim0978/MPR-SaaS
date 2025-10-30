#!/bin/bash

# Training Script: Llama 3.1 8B - Wikidata + Wikipedia Only (NO KILT WOW)

# Add all NVIDIA library paths
NVIDIA_LIBS="/usr/local/lib/python3.12/site-packages/nvidia/cusparselt/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvshmem/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvjitlink/lib:/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufile/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvtx/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparse/lib:/usr/local/lib/python3.12/site-packages/nvidia/curand/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufft/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusolver/lib"
export LD_LIBRARY_PATH=$NVIDIA_LIBS:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export HF_HOME=/home/hf_cache
export TRANSFORMERS_CACHE=/home/hf_cache
export CUDA_VISIBLE_DEVICES=1
export WANDB_PROJECT="knowledge-wikidata-wikipedia-only"

LOG_DIR="/home/logs/knowledge_wiki_only"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/8b_training.log"

echo "╔═══════════════════════════════════════════════════════════════════════════╗" | tee "$LOG_FILE"
echo "║   Training Llama 3.1 8B - Wikidata + Wikipedia Only (NO KILT WOW)       ║" | tee -a "$LOG_FILE"
echo "╚═══════════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Started at: $(date)" | tee -a "$LOG_FILE"
echo "GPU: cuda:1" | tee -a "$LOG_FILE"
echo "Dataset: Wikidata + Wikipedia (24,982 samples)" | tee -a "$LOG_FILE"
echo "Output: /home/models/llama31_8b_knowledge_wiki_only_lora" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

cd /home/LLaMA-Factory || exit

llamafactory-cli train /home/configs/knowledge/8b_knowledge_wikidata_wikipedia_only.yaml >> "$LOG_FILE" 2>&1

echo "" | tee -a "$LOG_FILE"
echo "Finished at: $(date)" | tee -a "$LOG_FILE"
echo "╔═══════════════════════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║                       TRAINING COMPLETE                                   ║" | tee -a "$LOG_FILE"
echo "╚═══════════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"


