#!/bin/bash

# Set environment variables
export WANDB_DISABLED=true
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=0

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║            🎯 COMPREHENSIVE MODEL EVALUATION                               ║
╚═══════════════════════════════════════════════════════════════════════════╝

This script will evaluate all 6 fine-tuned models:

📝 Grammar Correction (JFLEG):
   • Original Llama 3.2 3B
   • Fine-tuned Llama 3.2 3B (JFLEG)
   • Original Llama 3.1 8B
   • Fine-tuned Llama 3.1 8B (JFLEG)

🔄 Paraphrasing (PAWS):
   • Original Llama 3.2 3B
   • Fine-tuned Llama 3.2 3B (Paraphrase)
   • Original Llama 3.1 8B
   • Fine-tuned Llama 3.1 8B (Paraphrase)

🧠 Knowledge (Wizard of Wikipedia):
   • Original Llama 3.2 3B
   • Fine-tuned Llama 3.2 3B (Knowledge)
   • Original Llama 3.1 8B
   • Fine-tuned Llama 3.1 8B (Knowledge)

📊 Test Setup:
   • 10 samples per task (quick comparison)
   • Side-by-side output comparison
   • GPU: cuda:0
   • Estimated time: ~30-45 minutes

EOF

read -p "Press Enter to start evaluation..."

echo ""
echo "🚀 Starting evaluation..."
echo ""

python3 /home/scripts/evaluation/evaluate_all_models.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Evaluation complete!"
    echo ""
    echo "📊 Displaying results..."
    echo ""
    python3 /home/scripts/evaluation/compare_results.py | tee /home/evaluation_comparison_report.txt
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "✅ EVALUATION FINISHED"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "📁 Files created:"
    echo "   • /home/evaluation_results_grammar.json"
    echo "   • /home/evaluation_results_paraphrase.json"
    echo "   • /home/evaluation_results_knowledge.json"
    echo "   • /home/evaluation_comparison_report.txt"
    echo ""
else
    echo ""
    echo "❌ Evaluation failed. Check the logs above for errors."
    echo ""
fi

