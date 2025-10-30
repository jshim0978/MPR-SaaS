#!/bin/bash

# Emergency Status Check Script
# Run this anytime to verify training is progressing correctly

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  Paraphrasing Fine-tuning Status Check                                ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if training is running
if ps aux | grep -q "llama32_3b_paraphrase_config.yaml" | grep -v grep; then
    echo "✅ 3B Training: RUNNING"
    
    # Get latest progress
    if [ -f /home/llama32_3b_paraphrase_training.log ]; then
        PROGRESS=$(tail -500 /home/llama32_3b_paraphrase_training.log | grep -E "%" | tail -1 | grep -oP '\d+%' | tail -1)
        echo "   Progress: $PROGRESS"
        STEPS=$(tail -500 /home/llama32_3b_paraphrase_training.log | grep -oP '\d+/28263' | tail -1)
        echo "   Steps: $STEPS"
    fi
elif ps aux | grep -q "llama31_8b_paraphrase_config.yaml" | grep -v grep; then
    echo "✅ 8B Training: RUNNING"
    echo "   (3B completed, 8B in progress)"
    
    if [ -f /home/llama31_8b_paraphrase_training.log ]; then
        PROGRESS=$(tail -500 /home/llama31_8b_paraphrase_training.log | grep -E "%" | tail -1 | grep -oP '\d+%' | tail -1)
        echo "   Progress: $PROGRESS"
    fi
else
    echo "⚠️  NO TRAINING RUNNING"
    echo "   Checking if completed..."
    
    if [ -f /home/models/llama31_8b_paraphrase_lora/adapter_model.safetensors ]; then
        echo "   ✅ BOTH MODELS COMPLETED!"
    elif [ -f /home/models/llama32_3b_paraphrase_lora/adapter_model.safetensors ]; then
        echo "   ⚠️  3B completed, but 8B not started!"
        echo "   Check monitor log below."
    else
        echo "   ❌ Training may have failed!"
    fi
fi

echo ""

# Check monitor status
if ps aux | grep -q "monitor_paraphrase_training.py" | grep -v grep; then
    echo "✅ Monitor: ACTIVE"
    if [ -f /home/paraphrase_training_monitor.log ]; then
        echo "   Last check:"
        tail -1 /home/paraphrase_training_monitor.log
    fi
else
    echo "❌ Monitor: NOT RUNNING"
    echo "   WARNING: 8B may not auto-start!"
fi

echo ""

# Check W&B
echo "🔗 W&B Dashboard:"
echo "   https://wandb.ai/prml-nlp/paraphrase-llama-comparison"

echo ""

# Check disk space
DISK_USAGE=$(df -h /home | tail -1 | awk '{print $5}')
echo "💾 Disk Usage: $DISK_USAGE"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  Quick Commands                                                        ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo "View 3B log: tail -f /home/llama32_3b_paraphrase_training.log"
echo "View 8B log: tail -f /home/llama31_8b_paraphrase_training.log"
echo "View monitor: tail -f /home/paraphrase_training_monitor.log"
echo "Re-run check: /home/check_training_status.sh"

