#!/bin/bash

# Set environment variables
export WANDB_DISABLED=true
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=0

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║              🎯 HHEM EVALUATION - FACTUAL ACCURACY TEST                   ║
╚═══════════════════════════════════════════════════════════════════════════╝

Testing models on factual accuracy and hallucination:
   • Original Llama 3.2 3B
   • 3B Combined (Wiki + Wikidata)
   • Original Llama 3.1 8B  
   • 8B Combined (Wiki + Wikidata)

📝 Test Setup:
   • 20 factual questions with known correct answers
   • Assessing: accuracy, hallucination, completeness
   • Comparing: all 4 models side-by-side

⏱️  Estimated time: ~20-30 minutes
🎯 Goal: Determine factual accuracy and hallucination rates

EOF

echo ""
echo "🚀 Starting HHEM evaluation..."
echo ""

python3 /home/scripts/evaluation/evaluate_hhem.py

if [ $? -eq 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "✅ HHEM EVALUATION COMPLETE"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "📁 Results saved to:"
    echo "   • /home/evaluation_hhem_results.json"
    echo ""
    echo "📊 Review the results to check for factual accuracy and hallucinations"
    echo ""
else
    echo ""
    echo "❌ Evaluation failed. Check the logs above for errors."
    echo ""
fi

