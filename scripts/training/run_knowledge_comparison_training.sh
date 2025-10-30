#!/bin/bash

# Master orchestration script for knowledge dataset comparison training
# Runs 3 phases sequentially with automatic monitoring

MASTER_LOG="/home/logs/knowledge_comparison/master_orchestration.log"
mkdir -p /home/logs/knowledge_comparison

exec > >(tee -a "$MASTER_LOG") 2>&1

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║          KNOWLEDGE DATASET COMPARISON - MASTER ORCHESTRATOR              ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This will run 3 phases of parallel training:"
echo "  Phase 1: Wikidata (3B + 8B) - ~8 hours"
echo "  Phase 2: Wikipedia (3B + 8B) - ~12 hours"
echo "  Phase 3: KILT WOW (3B + 8B) - ~12 hours"
echo ""
echo "Total estimated time: ~32 hours"
echo ""
echo "Started at: $(date)"
echo ""

# Function to wait for a training process to complete
wait_for_training() {
    local config_file=$1
    local phase_name=$2
    
    echo "⏳ Waiting for $phase_name to complete..."
    while ps aux | grep -v grep | grep "$config_file" > /dev/null; do
        sleep 60 # Check every minute
    done
    echo "✅ $phase_name completed!"
}

# ============================================================================
# PHASE 1: WIKIDATA TRAINING
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 PHASE 1: WIKIDATA TRAINING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Starting parallel training:"
echo "  GPU 0: Llama 3.2 3B Wikidata"
echo "  GPU 1: Llama 3.1 8B Wikidata"
echo ""
echo "Started at: $(date)"
echo ""

# Start both trainings in parallel
chmod +x /home/scripts/training/train_3b_wikidata_only.sh
chmod +x /home/scripts/training/train_8b_wikidata_only.sh

nohup bash /home/scripts/training/train_3b_wikidata_only.sh &
PID_3B_WIKIDATA=$!
echo "✅ 3B Wikidata started (PID: $PID_3B_WIKIDATA)"

nohup bash /home/scripts/training/train_8b_wikidata_only.sh &
PID_8B_WIKIDATA=$!
echo "✅ 8B Wikidata started (PID: $PID_8B_WIKIDATA)"

# Wait for both to complete
wait_for_training "3b_wikidata_only.yaml" "3B Wikidata"
wait_for_training "8b_wikidata_only.yaml" "8B Wikidata"

echo ""
echo "✅ PHASE 1 COMPLETE!"
echo "Completed at: $(date)"
echo ""

# ============================================================================
# PHASE 2: WIKIPEDIA TRAINING
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 PHASE 2: WIKIPEDIA TRAINING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Starting parallel training:"
echo "  GPU 0: Llama 3.2 3B Wikipedia"
echo "  GPU 1: Llama 3.1 8B Wikipedia"
echo ""
echo "Started at: $(date)"
echo ""

# Start both trainings in parallel
chmod +x /home/scripts/training/train_3b_wikipedia_only.sh
chmod +x /home/scripts/training/train_8b_wikipedia_only.sh

nohup bash /home/scripts/training/train_3b_wikipedia_only.sh &
PID_3B_WIKIPEDIA=$!
echo "✅ 3B Wikipedia started (PID: $PID_3B_WIKIPEDIA)"

nohup bash /home/scripts/training/train_8b_wikipedia_only.sh &
PID_8B_WIKIPEDIA=$!
echo "✅ 8B Wikipedia started (PID: $PID_8B_WIKIPEDIA)"

# Wait for both to complete
wait_for_training "3b_wikipedia_only.yaml" "3B Wikipedia"
wait_for_training "8b_wikipedia_only.yaml" "8B Wikipedia"

echo ""
echo "✅ PHASE 2 COMPLETE!"
echo "Completed at: $(date)"
echo ""

# ============================================================================
# PHASE 3: KILT WOW TRAINING
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 PHASE 3: KILT WOW TRAINING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Starting parallel training:"
echo "  GPU 0: Llama 3.2 3B KILT WOW"
echo "  GPU 1: Llama 3.1 8B KILT WOW"
echo ""
echo "Started at: $(date)"
echo ""

# Start both trainings in parallel
chmod +x /home/scripts/training/train_3b_kilt_wow_only.sh
chmod +x /home/scripts/training/train_8b_kilt_wow_only.sh

nohup bash /home/scripts/training/train_3b_kilt_wow_only.sh &
PID_3B_KILT=$!
echo "✅ 3B KILT WOW started (PID: $PID_3B_KILT)"

nohup bash /home/scripts/training/train_8b_kilt_wow_only.sh &
PID_8B_KILT=$!
echo "✅ 8B KILT WOW started (PID: $PID_8B_KILT)"

# Wait for both to complete
wait_for_training "3b_kilt_wow_only.yaml" "3B KILT WOW"
wait_for_training "8b_kilt_wow_only.yaml" "8B KILT WOW"

echo ""
echo "✅ PHASE 3 COMPLETE!"
echo "Completed at: $(date)"
echo ""

# ============================================================================
# ALL PHASES COMPLETE
# ============================================================================
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║              ✅ ALL KNOWLEDGE COMPARISON TRAINING COMPLETE!               ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Trained Models (6 total):"
echo "  ✅ Llama 3.2 3B Wikidata"
echo "  ✅ Llama 3.1 8B Wikidata"
echo "  ✅ Llama 3.2 3B Wikipedia"
echo "  ✅ Llama 3.1 8B Wikipedia"
echo "  ✅ Llama 3.2 3B KILT WOW"
echo "  ✅ Llama 3.1 8B KILT WOW"
echo ""
echo "Model Directories:"
echo "  /home/models/llama32_3b_wikidata_only_lora"
echo "  /home/models/llama31_8b_wikidata_only_lora"
echo "  /home/models/llama32_3b_wikipedia_only_lora"
echo "  /home/models/llama31_8b_wikipedia_only_lora"
echo "  /home/models/llama32_3b_kilt_wow_only_lora"
echo "  /home/models/llama31_8b_kilt_wow_only_lora"
echo ""
echo "Logs:"
echo "  /home/logs/knowledge_comparison/"
echo ""
echo "W&B Project:"
echo "  https://wandb.ai/prml-nlp/knowledge-dataset-comparison"
echo ""
echo "🎯 NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1. Run knowledge dataset comparison evaluation"
echo "  2. Analyze paraphrase dataset comparison results"
echo "  3. Update colleague presentation materials"
echo ""
echo "Completed at: $(date)"
echo ""

