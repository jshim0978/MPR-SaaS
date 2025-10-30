#!/bin/bash

# Set environment variables
export WANDB_DISABLED=true
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=0

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║         🧠 COMBINED MODEL INFORMATIVE EVALUATION                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

Testing Wikipedia + Wikidata combined models:
   • Original Llama 3.2 3B
   • 3B Combined (Wiki + Wikidata)
   • Original Llama 3.1 8B  
   • 8B Combined (Wiki + Wikidata)

📝 Test Focus:
   • 25 prompts designed to elicit informative, factual responses
   • Testing for: specific facts, statistics, detailed explanations
   • Comparing: conversational vs informative style

⏱️  Estimated time: ~30-40 minutes
🎯 Goal: Determine if combined models produce the informative descriptions you want

EOF

echo ""
echo "🚀 Starting evaluation..."
echo ""

python3 /home/scripts/evaluation/evaluate_combined_informative.py

if [ $? -eq 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "✅ EVALUATION COMPLETE"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "📁 Results saved to:"
    echo "   • /home/evaluation_combined_informative.json"
    echo ""
    echo "📊 Check the sample outputs above, or review the full JSON file"
    echo ""
else
    echo ""
    echo "❌ Evaluation failed. Check the logs above for errors."
    echo ""
fi

