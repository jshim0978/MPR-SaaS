#!/bin/bash

# Quick Training Status Monitor
# Shows current progress of all trainings

clear

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║           📊 TRAINING STATUS MONITOR                                      ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF

echo ""
echo "🔄 ACTIVE TRAININGS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check running processes
RUNNING=$(ps aux | grep llamafactory-cli | grep -v grep | wc -l)

if [ $RUNNING -eq 0 ]; then
    echo "  ⚠️  No training processes running!"
else
    ps aux | grep llamafactory-cli | grep -v grep | while read line; do
        if echo "$line" | grep -q "3b_qqp_only"; then
            echo "  🔄 3B QQP-only (GPU 1)"
        elif echo "$line" | grep -q "8b_qqp_only"; then
            echo "  🔄 8B QQP-only (GPU 0)"
        elif echo "$line" | grep -q "8b_paws_only"; then
            echo "  🔄 8B PAWS-only (GPU 1)"
        fi
    done
fi

echo ""
echo "🤖 AUTO-SCHEDULER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if ps aux | grep -q "auto_start_phase2.sh" | grep -v grep; then
    echo "  ✅ Scheduler ACTIVE - monitoring for 3B QQP completion"
else
    echo "  ⚠️  Scheduler NOT running"
fi

echo ""
echo "🖥️  GPU STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader | while IFS=',' read -r gpu name util mem_used mem_total; do
    echo "  GPU $gpu: ${util% *}% utilization, ${mem_used% *}/${mem_total% *} memory"
done

echo ""
echo "📊 TRAINING PROGRESS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check 3B QQP progress
if [ -f "/home/logs/dataset_comparison/llama32_3b_qqp_only_training.log" ]; then
    LAST_3B=$(tail -20 /home/logs/dataset_comparison/llama32_3b_qqp_only_training.log 2>/dev/null | grep -oP '\d+%' | tail -1)
    if [ -n "$LAST_3B" ]; then
        echo "  3B QQP-only:  $LAST_3B complete"
    else
        echo "  3B QQP-only:  Running..."
    fi
fi

# Check 8B QQP progress
if [ -f "/home/logs/dataset_comparison/llama31_8b_qqp_only_training.log" ]; then
    LAST_8B=$(tail -20 /home/logs/dataset_comparison/llama31_8b_qqp_only_training.log 2>/dev/null | grep -oP '\d+%' | tail -1)
    if [ -n "$LAST_8B" ]; then
        echo "  8B QQP-only:  $LAST_8B complete"
    else
        echo "  8B QQP-only:  Running..."
    fi
fi

# Check if 8B PAWS has started
if [ -f "/home/logs/dataset_comparison/llama31_8b_paws_only_training.log" ]; then
    LAST_PAWS=$(tail -20 /home/logs/dataset_comparison/llama31_8b_paws_only_training.log 2>/dev/null | grep -oP '\d+%' | tail -1)
    if [ -n "$LAST_PAWS" ]; then
        echo "  8B PAWS-only: $LAST_PAWS complete"
    else
        echo "  8B PAWS-only: Running..."
    fi
else
    echo "  8B PAWS-only: Queued (waiting for 3B QQP)"
fi

echo ""
echo "✅ COMPLETED MODELS: 7/10"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✅ llama32_3b_grammar_lora"
echo "  ✅ llama31_8b_grammar_lora"
echo "  ✅ llama32_3b_paraphrase_lora"
echo "  ✅ llama31_8b_paraphrase_lora"
echo "  ✅ llama32_3b_knowledge_lora"
echo "  ✅ llama31_8b_knowledge_lora"
echo "  ✅ llama32_3b_paws_only_lora"
echo ""
echo "📋 QUICK COMMANDS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Watch this monitor:     watch -n 60 /home/scripts/monitoring/training_status.sh"
echo "  Check scheduler log:    tail -f /home/logs/dataset_comparison/phase2_scheduler.log"
echo "  Check 3B QQP log:       tail -f /home/logs/dataset_comparison/llama32_3b_qqp_only_training.log"
echo "  Check 8B QQP log:       tail -f /home/logs/dataset_comparison/llama31_8b_qqp_only_training.log"
echo "  GPU status:             nvidia-smi"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

