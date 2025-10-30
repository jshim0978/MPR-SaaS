#!/bin/bash

# Prepare Individual Knowledge Datasets
# Creates: wikidata_only, wikipedia_only, kilt_wow_only

# Add all NVIDIA library paths
NVIDIA_LIBS="/usr/local/lib/python3.12/site-packages/nvidia/cusparselt/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvshmem/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvjitlink/lib:/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufile/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvtx/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparse/lib:/usr/local/lib/python3.12/site-packages/nvidia/curand/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufft/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusolver/lib"
export LD_LIBRARY_PATH=$NVIDIA_LIBS:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export HF_HOME=/home/hf_cache
export TRANSFORMERS_CACHE=/home/hf_cache

LOG_FILE="/home/logs/prepare_individual_knowledge_datasets.log"

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║        PREPARING INDIVIDUAL KNOWLEDGE DATASETS                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Creating three datasets:"
echo "  1. Wikidata-only (~10k examples)"
echo "  2. Wikipedia-only (~15k examples)"
echo "  3. KILT WOW-only (~15k examples)"
echo ""
echo "Log: $LOG_FILE"
echo ""

cd /home
python3 scripts/dataset_prep/prepare_individual_knowledge_datasets.py 2>&1 | tee "$LOG_FILE"

echo ""
echo "✅ Dataset preparation complete!"

