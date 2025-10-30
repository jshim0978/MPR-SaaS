#!/bin/bash
# Quick Reference: Knowledge Training Commands

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║             KNOWLEDGE TRAINING - QUICK REFERENCE CARD                     ║
╚═══════════════════════════════════════════════════════════════════════════╝

🚀 ONE-COMMAND LAUNCH (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  /home/start_knowledge_training.sh

  ↳ Does everything: prep datasets + start both trainings

🔧 MANUAL STEPS (If you prefer control)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # 1. Prepare datasets
  /home/prepare_all_knowledge_datasets.sh

  # 2. Start 3B training (GPU 0)
  nohup /home/run_llama32_3b_knowledge_training.sh > /home/llama32_3b_knowledge_training.log 2>&1 &

  # 3. Start 8B training (GPU 1)
  nohup /home/run_llama31_8b_knowledge_training.sh > /home/llama31_8b_knowledge_training.log 2>&1 &

📊 MONITORING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # W&B Dashboard
  https://wandb.ai/jshim0978/knowledge-llama-enhancement

  # View 3B log
  tail -f /home/llama32_3b_knowledge_training.log

  # View 8B log
  tail -f /home/llama31_8b_knowledge_training.log

  # Check GPU usage
  nvidia-smi

  # Check if training is running
  pgrep -fa llamafactory.*knowledge

🔍 STATUS CHECKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # Check progress percentage
  tail -100 /home/llama32_3b_knowledge_training.log | grep -oP '\d+%' | tail -1
  tail -100 /home/llama31_8b_knowledge_training.log | grep -oP '\d+%' | tail -1

  # Check if models exist
  ls -lh /home/models/llama32_3b_knowledge_lora/adapter_model.safetensors
  ls -lh /home/models/llama31_8b_knowledge_lora/adapter_model.safetensors

📁 IMPORTANT PATHS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Datasets:
    /home/data/knowledge_combined.json

  Models:
    /home/models/llama32_3b_knowledge_lora/
    /home/models/llama31_8b_knowledge_lora/

  Logs:
    /home/llama32_3b_knowledge_training.log
    /home/llama31_8b_knowledge_training.log

  Documentation:
    /home/KNOWLEDGE_TRAINING_PLAN.md
    /home/KNOWLEDGE_READY_SUMMARY.md

⏱️  EXPECTED TIMELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Dataset Preparation:  ~1 hour
  3B Training (GPU 0):  ~6 hours
  8B Training (GPU 1):  ~8 hours
  ─────────────────────────────────
  Total (parallel):     ~9 hours

🎯 DATASETS INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Wikidata:    50,000 entity descriptions
  • Wikipedia:   20,000 article summaries
  • KILT WoW:    30,000 knowledge dialogues
  ────────────────────────────────────────
  Total:        ~100,000 examples

✅ COMPLETION CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  When both log files show "✅ Training completed!", you're done!

  Final models:
    ✅ Llama 3.2 3B - Grammar
    ✅ Llama 3.2 3B - Paraphrasing
    ✅ Llama 3.2 3B - Knowledge
    ✅ Llama 3.1 8B - Grammar
    ✅ Llama 3.1 8B - Paraphrasing
    ✅ Llama 3.1 8B - Knowledge

  = 6 specialized models ready! 🎉

╔═══════════════════════════════════════════════════════════════════════════╗
║            Everything is ready. Just run when paraphrasing done!          ║
╚═══════════════════════════════════════════════════════════════════════════╝

EOF

