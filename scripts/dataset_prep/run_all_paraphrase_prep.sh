#!/bin/bash

# Master script to prepare paraphrasing datasets
# Runs PAWS preparation, QQP preparation, and combines them

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  Preparing Paraphrasing Datasets (PAWS + QQP)                         ║"
echo "║  Strategy: Bidirectional Generation (Option C)                        ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Set environment
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"

echo "📦 Step 1/3: Preparing PAWS dataset..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 /home/scripts/dataset_prep/prep_paws.py
echo ""

echo "📦 Step 2/3: Preparing QQP dataset..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 /home/scripts/dataset_prep/prep_qqp.py
echo ""

echo "🔀 Step 3/3: Combining datasets..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 /home/scripts/dataset_prep/combine_paraphrase.py
echo ""

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ All datasets prepared successfully!                                ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Output files in /home/data/:"
echo "   • paraphrase_combined_train.jsonl"
echo "   • paraphrase_combined_eval.jsonl"
echo "   • paraphrase_combined_test.jsonl"
echo "   • paraphrase_combined.json (for LLaMA-Factory)"
echo ""
echo "🎯 Next step: Update LLaMA-Factory dataset_info.json and start training!"

