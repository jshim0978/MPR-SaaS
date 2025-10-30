#!/bin/bash

# Optimized Phase 2 auto-scheduler
# GPU 0 finished first, so start 8B QQP there immediately
# GPU 1 will start 8B PAWS once current 3B QQP finishes

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║           OPTIMIZED PHASE 2 AUTO-SCHEDULER                                ║
╚═══════════════════════════════════════════════════════════════════════════╝

🎯 OPTIMIZED STRATEGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  GPU 0 finished first → Start 8B QQP-only NOW (longest training, ~14h)
  GPU 1 finishing soon → Auto-start 8B PAWS-only when ready (~6h)

This maximizes efficiency by starting the longest training immediately!

📊 TRAINING SCHEDULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  NOW:    GPU 0: 8B QQP-only    (~14 hours)
  SOON:   GPU 1: 8B PAWS-only   (~6 hours) [Auto-start when GPU 1 free]

Total Phase 2 time: ~14 hours (vs 20h if we waited for both to finish)

EOF

# Start 8B QQP on GPU 0 immediately
echo ""
echo "🚀 Starting 8B QQP-only on GPU 0 (freed up)..."
nohup /home/scripts/training/train_8b_qqp_only.sh > /home/logs/dataset_comparison/llama31_8b_qqp_only_training.log 2>&1 &
PID_8B_QQP=$!
echo "✅ 8B QQP started on GPU 0 (PID: $PID_8B_QQP)"

sleep 5

# Check if it started successfully
if ps -p $PID_8B_QQP > /dev/null; then
    echo "✅ 8B QQP training confirmed running on GPU 0"
else
    echo "❌ Failed to start 8B QQP training"
    exit 1
fi

echo ""
echo "🔄 Monitoring GPU 1 for completion of 3B QQP..."
echo "   Will auto-start 8B PAWS when GPU 1 becomes available"
echo ""

# Wait for GPU 1 to become free (3B QQP to finish)
while true; do
    # Check if 3B QQP process is still running
    if ! pgrep -f "3b_qqp_only.yaml" > /dev/null; then
        echo ""
        echo "✅ GPU 1 is now free! Starting 8B PAWS-only..."
        sleep 2
        
        nohup /home/scripts/training/train_8b_paws_only.sh > /home/logs/dataset_comparison/llama31_8b_paws_only_training.log 2>&1 &
        PID_8B_PAWS=$!
        echo "✅ 8B PAWS started on GPU 1 (PID: $PID_8B_PAWS)"
        
        sleep 5
        
        if ps -p $PID_8B_PAWS > /dev/null; then
            echo "✅ 8B PAWS training confirmed running on GPU 1"
        else
            echo "❌ Failed to start 8B PAWS training"
            exit 1
        fi
        
        break
    fi
    
    # Wait 30 seconds before checking again
    sleep 30
done

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ PHASE 2 FULLY RUNNING!                                ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 BOTH 8B MODELS NOW TRAINING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  GPU 0: 8B QQP-only  (PID: $PID_8B_QQP) - ~14 hours"
echo "  GPU 1: 8B PAWS-only (PID: $PID_8B_PAWS) - ~6 hours"
echo ""
echo "🔗 MONITORING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  W&B: https://wandb.ai/prml-nlp/paraphrase-dataset-comparison"
echo "  Logs:"
echo "    tail -f /home/logs/dataset_comparison/llama31_8b_qqp_only_training.log"
echo "    tail -f /home/logs/dataset_comparison/llama31_8b_paws_only_training.log"
echo "  GPU: nvidia-smi"
echo ""
echo "⏱️  ESTIMATED COMPLETION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 2 complete in ~14 hours (longest training)"
echo "  All dataset comparison training complete!"
echo ""

