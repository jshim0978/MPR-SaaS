#!/bin/bash

# Deep Repository Cleanup - Phase 2
# Remove all duplicates, old versions, and unused files

set -e

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║                   DEEP CLEANUP - PHASE 2                                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

This will remove:
  • Duplicate/old dataset versions (jfleg_clean, jfleg_improved)
  • Raw arrow files in data/jfleg/
  • Unused eval/test splits (we use val_size instead)
  • Individual component files (already combined)
  • Old model directories with wrong names
  • Alternate/duplicate training scripts
  • Misplaced log files

EOF

echo "🗑️  Starting deep cleanup..."
echo ""

# ============================================================================
# CLEAN DATA DIRECTORY
# ============================================================================

echo "📁 Cleaning /home/data/"
echo ""

# Remove old JFLEG versions
if [ -f "/home/data/jfleg_clean_train.jsonl" ]; then
    echo "  → Removing jfleg_clean_*.jsonl (replaced by jfleg_all_corrections)"
    rm -f /home/data/jfleg_clean_train.jsonl
    rm -f /home/data/jfleg_clean_eval.jsonl
    rm -f /home/data/jfleg_clean_test.jsonl
fi

if [ -f "/home/data/jfleg_improved_train.jsonl" ]; then
    echo "  → Removing jfleg_improved_*.jsonl (experimental, not used)"
    rm -f /home/data/jfleg_improved_train.jsonl
    rm -f /home/data/jfleg_improved_eval.jsonl
    rm -f /home/data/jfleg_improved_test.jsonl
fi

# Remove raw JFLEG arrow files
if [ -d "/home/data/jfleg" ]; then
    echo "  → Removing /home/data/jfleg/ (raw arrow files, not needed)"
    rm -rf /home/data/jfleg
fi

# Remove unused eval/test splits (we use val_size now)
echo "  → Removing unused eval/test splits (using val_size instead)"
rm -f /home/data/paraphrase_combined_eval.jsonl
rm -f /home/data/paraphrase_combined_test.jsonl
rm -f /home/data/paws_paraphrase_eval.jsonl
rm -f /home/data/paws_paraphrase_test.jsonl
rm -f /home/data/jfleg_all_corrections_eval.jsonl
rm -f /home/data/jfleg_all_corrections_test.jsonl

# Remove individual component files (already combined)
echo "  → Removing individual component files (already in combined datasets)"
rm -f /home/data/wikidata_knowledge.jsonl
rm -f /home/data/wikipedia_knowledge.jsonl
rm -f /home/data/kilt_wow_knowledge.jsonl

# ============================================================================
# CLEAN MODELS DIRECTORY
# ============================================================================

echo ""
echo "📁 Cleaning /home/models/"
echo ""

# Rename old model directories to proper names
if [ -d "/home/models/llama32_3b_lora_factory" ]; then
    echo "  → Renaming llama32_3b_lora_factory → llama32_3b_grammar_lora"
    mv /home/models/llama32_3b_lora_factory /home/models/llama32_3b_grammar_lora
fi

if [ -d "/home/models/llama31_8b_lora_factory" ]; then
    echo "  → Renaming llama31_8b_lora_factory → llama31_8b_grammar_lora"
    mv /home/models/llama31_8b_lora_factory /home/models/llama31_8b_grammar_lora
fi

# ============================================================================
# CLEAN SCRIPTS DIRECTORY
# ============================================================================

echo ""
echo "📁 Cleaning /home/scripts/"
echo ""

# Remove alternate/unused training scripts
if [ -f "/home/scripts/training/train_3b_grammar_alt.sh" ]; then
    echo "  → Removing train_3b_grammar_alt.sh (alternate version, not used)"
    rm -f /home/scripts/training/train_3b_grammar_alt.sh
fi

if [ -f "/home/scripts/training/train_8b_grammar_alt.sh" ]; then
    echo "  → Removing train_8b_grammar_alt.sh (alternate version, not used)"
    rm -f /home/scripts/training/train_8b_grammar_alt.sh
fi

# ============================================================================
# CLEAN LOGS DIRECTORY
# ============================================================================

echo ""
echo "📁 Cleaning /home/logs/"
echo ""

# Move misplaced logs to proper subdirectories
if [ -f "/home/logs/llama31_8b_lora_training.log" ]; then
    echo "  → Moving llama31_8b_lora_training.log → logs/grammar/"
    mv /home/logs/llama31_8b_lora_training.log /home/logs/grammar/8b_grammar_training.log
fi

if [ -f "/home/logs/llama32_3b_lora_factory_training.log" ]; then
    echo "  → Moving llama32_3b_lora_factory_training.log → logs/grammar/"
    mv /home/logs/llama32_3b_lora_factory_training.log /home/logs/grammar/3b_grammar_training.log
fi

if [ -f "/home/logs/llama32_3b_lora_training.log" ]; then
    echo "  → Removing llama32_3b_lora_training.log (duplicate)"
    rm -f /home/logs/llama32_3b_lora_training.log
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ DEEP CLEANUP COMPLETE!                                ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Data directory:"
echo "  • Removed 6 duplicate JFLEG files"
echo "  • Removed raw arrow files"
echo "  • Removed 6 unused eval/test splits"
echo "  • Removed 3 component files (already combined)"
echo ""
echo "Models directory:"
echo "  • Renamed 2 models to proper naming convention"
echo ""
echo "Scripts directory:"
echo "  • Removed 2 alternate training scripts"
echo ""
echo "Logs directory:"
echo "  • Moved 2 logs to proper subdirectories"
echo "  • Removed 1 duplicate log"
echo ""
echo "✅ Repository is now maximally clean and tidy!"
echo ""

