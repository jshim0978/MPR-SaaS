#!/bin/bash

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║           PARAPHRASE DATASET COMPARISON - TRAINING SCHEDULE               ║
╚═══════════════════════════════════════════════════════════════════════════╝

This script will run PAWS-only and QQP-only training for comparison analysis.

📊 DATASET SIZES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  PAWS only:     43,658 examples (30% of combined)
  QQP only:     100,000 examples (70% of combined)
  Combined:     143,658 examples (already training)

🎯 TRAINING PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After current 8B trainings complete, we'll run:

Phase 1 (Parallel on both GPUs):
  • GPU 0: 3B PAWS-only    (~3 hours)
  • GPU 1: 3B QQP-only     (~6 hours)

Phase 2 (Parallel on both GPUs):
  • GPU 0: 8B PAWS-only    (~6 hours)
  • GPU 1: 8B QQP-only     (~14 hours)

Total additional time: ~20 hours

📁 OUTPUT MODELS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  /home/models/llama32_3b_paws_only_lora/
  /home/models/llama32_3b_qqp_only_lora/
  /home/models/llama31_8b_paws_only_lora/
  /home/models/llama31_8b_qqp_only_lora/

🔗 W&B PROJECT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  https://wandb.ai/prml-nlp/paraphrase-dataset-comparison

📋 COMPARISON ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After training completes, you'll be able to compare:
  • PAWS-only vs QQP-only vs Combined
  • Performance on different paraphrase types
  • Dataset size impact on quality

EOF

read -p "Start Phase 1 now (3B models)? [y/N]: " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting Phase 1: 3B Models (PAWS & QQP)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "Starting 3B PAWS-only on GPU 0..."
    nohup /home/scripts/training/train_3b_paws_only.sh > /dev/null 2>&1 &
    PID_3B_PAWS=$!
    echo "✅ 3B PAWS started (PID: $PID_3B_PAWS)"
    
    sleep 2
    
    echo "Starting 3B QQP-only on GPU 1..."
    nohup /home/scripts/training/train_3b_qqp_only.sh > /dev/null 2>&1 &
    PID_3B_QQP=$!
    echo "✅ 3B QQP started (PID: $PID_3B_QQP)"
    
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════╗"
    echo "║                   ✅ PHASE 1 STARTED!                                      ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Monitor progress:"
    echo "  • W&B: https://wandb.ai/prml-nlp/paraphrase-dataset-comparison"
    echo "  • Logs: tail -f /home/llama32_3b_paws_only_training.log"
    echo "  •       tail -f /home/llama32_3b_qqp_only_training.log"
    echo ""
    echo "When Phase 1 completes, run this script again for Phase 2 (8B models)"
else
    echo ""
    echo "Canceled. Run this script when ready to start training."
    echo ""
    echo "To manually start trainings:"
    echo "  Phase 1 (3B):"
    echo "    /home/scripts/training/train_3b_paws_only.sh  # GPU 0"
    echo "    /home/scripts/training/train_3b_qqp_only.sh   # GPU 1"
    echo ""
    echo "  Phase 2 (8B):"
    echo "    /home/scripts/training/train_8b_paws_only.sh  # GPU 0"
    echo "    /home/scripts/training/train_8b_qqp_only.sh   # GPU 1"
fi

