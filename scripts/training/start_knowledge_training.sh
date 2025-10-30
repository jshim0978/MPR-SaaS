#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                     KNOWLEDGE TRAINING - QUICK START                      ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will prepare datasets and start knowledge enhancement training"
echo "for both Llama 3.2 3B and Llama 3.1 8B models."
echo ""
echo "⏱️  Total estimated time: ~7-9 hours (1h prep + 6-8h training)"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Step 1: Prepare datasets
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/3: Preparing Knowledge Datasets"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
/home/prepare_all_knowledge_datasets.sh

if [ $? -ne 0 ]; then
    echo "❌ Dataset preparation failed!"
    exit 1
fi

# Step 2: Start 3B training
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/3: Starting Llama 3.2 3B Training (GPU 0)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
nohup /home/run_llama32_3b_knowledge_training.sh > /dev/null 2>&1 &
PID_3B=$!
echo "✅ Llama 3.2 3B training started (PID: $PID_3B)"

# Step 3: Start 8B training
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3/3: Starting Llama 3.1 8B Training (GPU 1)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
nohup /home/run_llama31_8b_knowledge_training.sh > /dev/null 2>&1 &
PID_8B=$!
echo "✅ Llama 3.1 8B training started (PID: $PID_8B)"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                     ✅ ALL SYSTEMS GO!                                     ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 W&B Dashboard: https://wandb.ai/jshim0978/knowledge-llama-enhancement"
echo ""
echo "📝 Monitor logs:"
echo "   3B: tail -f /home/llama32_3b_knowledge_training.log"
echo "   8B: tail -f /home/llama31_8b_knowledge_training.log"
echo ""
echo "🖥️  Check GPU usage:"
echo "   nvidia-smi"
echo ""
echo "⏱️  Expected completion: ~6-8 hours from now"
echo ""
echo "📁 Models will be saved to:"
echo "   3B: /home/models/llama32_3b_knowledge_lora"
echo "   8B: /home/models/llama31_8b_knowledge_lora"
echo ""

