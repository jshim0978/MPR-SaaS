#!/bin/bash

# Automatic Phase Manager - Runs all 3 phases sequentially
# Phase 1: Wikidata → Phase 2: Wikipedia → Phase 3: KILT WOW

LOG_FILE="/home/logs/knowledge_comparison/auto_phase_manager.log"
mkdir -p /home/logs/knowledge_comparison

exec > >(tee -a "$LOG_FILE") 2>&1

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║              AUTOMATIC PHASE MANAGER - STARTED                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Started at: $(date)"
echo ""

# Function to wait for specific configs to finish
wait_for_configs() {
    local config1=$1
    local config2=$2
    local phase_name=$3
    
    echo "⏳ Waiting for $phase_name to complete..."
    while ps aux | grep -v grep | grep -E "$config1|$config2" > /dev/null; do
        sleep 300 # Check every 5 minutes
        echo "[$(date)] $phase_name still running..." >> "$LOG_FILE"
    done
    echo "✅ $phase_name completed at $(date)"
}

# ============================================================================
# PHASE 1: WIKIDATA (Already running)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 PHASE 1: WIKIDATA TRAINING (Already Started)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

wait_for_configs "3b_wikidata_only.yaml" "8b_wikidata_only.yaml" "Phase 1 (Wikidata)"

echo ""
echo "✅ PHASE 1 COMPLETE!"
echo ""

# ============================================================================
# PHASE 2: WIKIPEDIA
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 PHASE 2: WIKIPEDIA TRAINING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Starting at: $(date)"
echo ""

cd /home
bash scripts/training/train_3b_wikipedia_only.sh > /dev/null 2>&1 &
PID_3B_WIKI=$!
echo "✅ 3B Wikipedia started (PID: $PID_3B_WIKI)"

bash scripts/training/train_8b_wikipedia_only.sh > /dev/null 2>&1 &
PID_8B_WIKI=$!
echo "✅ 8B Wikipedia started (PID: $PID_8B_WIKI)"

wait_for_configs "3b_wikipedia_only.yaml" "8b_wikipedia_only.yaml" "Phase 2 (Wikipedia)"

echo ""
echo "✅ PHASE 2 COMPLETE!"
echo ""

# ============================================================================
# PHASE 3: KILT WOW
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 PHASE 3: KILT WOW TRAINING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Starting at: $(date)"
echo ""

cd /home
bash scripts/training/train_3b_kilt_wow_only.sh > /dev/null 2>&1 &
PID_3B_KILT=$!
echo "✅ 3B KILT WOW started (PID: $PID_3B_KILT)"

bash scripts/training/train_8b_kilt_wow_only.sh > /dev/null 2>&1 &
PID_8B_KILT=$!
echo "✅ 8B KILT WOW started (PID: $PID_8B_KILT)"

wait_for_configs "3b_kilt_wow_only.yaml" "8b_kilt_wow_only.yaml" "Phase 3 (KILT WOW)"

echo ""
echo "✅ PHASE 3 COMPLETE!"
echo ""

# ============================================================================
# ALL PHASES COMPLETE
# ============================================================================
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║              ✅ ALL 3 PHASES COMPLETE!                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Completed at: $(date)"
echo ""
echo "📊 TRAINED MODELS (6 total)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Phase 1 (Wikidata):"
echo "  ✅ /home/models/llama32_3b_wikidata_only_lora"
echo "  ✅ /home/models/llama31_8b_wikidata_only_lora"
echo ""
echo "Phase 2 (Wikipedia):"
echo "  ✅ /home/models/llama32_3b_wikipedia_only_lora"
echo "  ✅ /home/models/llama31_8b_wikipedia_only_lora"
echo ""
echo "Phase 3 (KILT WOW):"
echo "  ✅ /home/models/llama32_3b_kilt_wow_only_lora"
echo "  ✅ /home/models/llama31_8b_kilt_wow_only_lora"
echo ""
echo "🔗 W&B Dashboard:"
echo "   https://wandb.ai/prml-nlp/knowledge-dataset-comparison"
echo ""
echo "🎯 NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1. Analyze paraphrase dataset comparison results"
echo "  2. Run knowledge dataset comparison evaluation"
echo "  3. Update colleague presentation materials"
echo ""

