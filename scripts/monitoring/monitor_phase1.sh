#!/bin/bash

# Monitor Phase 1 (Wikidata) training completion

LOG_FILE="/home/logs/knowledge_comparison/phase1_monitor.log"
PHASE1_3B_CONFIG="3b_wikidata_only.yaml"
PHASE1_8B_CONFIG="8b_wikidata_only.yaml"

echo "╔═══════════════════════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║              PHASE 1 MONITORING - WIKIDATA TRAINING                      ║" | tee -a "$LOG_FILE"
echo "╚═══════════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Started monitoring at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Wait for both trainings to complete
while ps aux | grep -v grep | grep "$PHASE1_3B_CONFIG\|$PHASE1_8B_CONFIG" > /dev/null; do
    # Check status every 5 minutes
    sleep 300
    
    # Log status
    echo "[$(date)] Phase 1 still running..." >> "$LOG_FILE"
    
    # Check GPU utilization
    nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader,nounits >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
done

echo "" | tee -a "$LOG_FILE"
echo "╔═══════════════════════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║                    ✅ PHASE 1 COMPLETE!                                   ║" | tee -a "$LOG_FILE"
echo "╚═══════════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Completed at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📊 RESULTS" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "✅ 3B Wikidata model saved to: /home/models/llama32_3b_wikidata_only_lora" | tee -a "$LOG_FILE"
echo "✅ 8B Wikidata model saved to: /home/models/llama31_8b_wikidata_only_lora" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📁 Logs:" | tee -a "$LOG_FILE"
echo "   /home/logs/knowledge_comparison/llama32_3b_wikidata_only_training.log" | tee -a "$LOG_FILE"
echo "   /home/logs/knowledge_comparison/llama31_8b_wikidata_only_training.log" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "🔗 W&B:" | tee -a "$LOG_FILE"
echo "   https://wandb.ai/prml-nlp/knowledge-dataset-comparison" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "🎯 NEXT STEP: Start Phase 2 (Wikipedia training)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

