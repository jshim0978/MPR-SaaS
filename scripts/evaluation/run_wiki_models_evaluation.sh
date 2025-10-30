#!/bin/bash

# Set environment variables
export WANDB_DISABLED=true
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"
export LD_LIBRARY_PATH="/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_cupti/lib:/usr/local/cuda-12.9/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
export CUDA_VISIBLE_DEVICES=0

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║         🧠 WIKIPEDIA-FOCUSED MODELS EVALUATION                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

Testing models trained WITHOUT KILT WOW:
   • 3B Wikipedia-only
   • 3B Wikidata-only
   • 3B Wiki+Wikidata (no KILT)
   • 8B Wikipedia-only
   • 8B Wikidata-only
   • 8B Wiki+Wikidata (no KILT)

📝 Test Setup:
   • 20 factual questions (HHEM benchmark)
   • Assessing: detail, accuracy, informativeness
   • Excluding: conversational/dialogue models

⏱️  Estimated time: ~30-40 minutes
🎯 Goal: Find models that provide detailed, factual, non-conversational responses

EOF

echo ""
echo "🚀 Starting evaluation..."
echo ""

python3 /home/scripts/evaluation/evaluate_wiki_models_only.py

if [ $? -eq 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "✅ EVALUATION COMPLETE"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "📁 Results saved to:"
    echo "   • /home/evaluation_wiki_models_only.json"
    echo ""
    echo "📊 Running analysis..."
    echo ""
    python3 /home/scripts/evaluation/analyze_wiki_models.py
else
    echo ""
    echo "❌ Evaluation failed. Check the logs above for errors."
    echo ""
fi

