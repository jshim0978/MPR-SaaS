#!/bin/bash

# Repository Cleanup Script
# Removes all junk and keeps only essentials

set -e

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║                   REPOSITORY CLEANUP - REMOVING JUNK                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

This script will remove:
  • Old/failed scripts in archive directories
  • Temporary logs in root directory
  • MPR temporary files and wandb runs
  • Duplicate/obsolete training logs
  • Old organizational scripts
  • llf_runs directory (not used)
  • training_logs directory (empty/unused)

Will keep:
  ✅ /configs/ - All training configurations
  ✅ /scripts/ - Working scripts (dataset_prep, evaluation, training, monitoring)
  ✅ /data/ - All prepared datasets
  ✅ /docs/ - Documentation
  ✅ /logs/ - Organized logs (grammar, paraphrase, knowledge, monitoring)
  ✅ /models/ - Fine-tuned model weights
  ✅ /LLaMA-Factory/ - Training framework
  ✅ /hf_cache/ - Hugging Face cache
  ✅ README.md, QUICK_REFERENCE.txt, requirements.txt

EOF

read -p "Proceed with cleanup? [y/N]: " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup canceled."
    exit 0
fi

echo ""
echo "🗑️  Starting cleanup..."
echo ""

# Remove archive directories (old/failed/test scripts)
if [ -d "/home/archive" ]; then
    echo "  → Removing /home/archive/ (old scripts)"
    rm -rf /home/archive
fi

if [ -d "/home/archive_failed_scripts" ]; then
    echo "  → Removing /home/archive_failed_scripts/"
    rm -rf /home/archive_failed_scripts
fi

if [ -d "/home/archive_old_scripts" ]; then
    echo "  → Removing /home/archive_old_scripts/"
    rm -rf /home/archive_old_scripts
fi

if [ -d "/home/archive_test_scripts" ]; then
    echo "  → Removing /home/archive_test_scripts/"
    rm -rf /home/archive_test_scripts
fi

# Remove unused directories
if [ -d "/home/llf_runs" ]; then
    echo "  → Removing /home/llf_runs/ (unused)"
    rm -rf /home/llf_runs
fi

if [ -d "/home/training_logs" ]; then
    echo "  → Removing /home/training_logs/ (unused)"
    rm -rf /home/training_logs
fi

# Remove MPR temporary files
if [ -d "/home/mpr/tmp" ]; then
    echo "  → Removing /home/mpr/tmp/ (temporary wandb files)"
    rm -rf /home/mpr/tmp
fi

if [ -d "/home/mpr/wandb" ]; then
    echo "  → Removing /home/mpr/wandb/ (old wandb runs)"
    rm -rf /home/mpr/wandb
fi

if [ -d "/home/mpr/pip_cache" ]; then
    echo "  → Removing /home/mpr/pip_cache/"
    rm -rf /home/mpr/pip_cache
fi

if [ -d "/home/mpr/llf_runs" ]; then
    echo "  → Removing /home/mpr/llf_runs/"
    rm -rf /home/mpr/llf_runs
fi

if [ -d "/home/mpr/llf_data" ]; then
    echo "  → Removing /home/mpr/llf_data/"
    rm -rf /home/mpr/llf_data
fi

# Remove entire MPR directory if empty
if [ -d "/home/mpr" ]; then
    if [ -z "$(ls -A /home/mpr)" ]; then
        echo "  → Removing empty /home/mpr/ directory"
        rm -rf /home/mpr
    fi
fi

# Remove old logs from root directory
echo "  → Removing old log files from root"
rm -f /home/knowledge_prep.log
rm -f /home/llama31_8b_qqp_only_training.log
rm -f /home/llama32_3b_paws_only_training.log
rm -f /home/llama32_3b_qqp_only_training.log
rm -f /home/monitor.log
rm -f /home/monitor_8b.log
rm -f /home/paraphrase_monitor.log
rm -f /home/paraphrase_training_monitor.log
rm -f /home/training_monitor_8b.log
rm -f /home/watchdog.log

# Remove organizational scripts (no longer needed)
echo "  → Removing temporary organizational scripts"
rm -f /home/organize_logs.sh
rm -f /home/organize_repository.sh
rm -f /home/update_references.sh

# Remove old status markdown files
echo "  → Removing old status documents"
rm -f /home/DATASET_COMPARISON_TRAINING_STATUS.md
rm -f /home/ORGANIZATION_SUMMARY.md

# Clean up empty directories in logs/
if [ -d "/home/logs/archive" ]; then
    if [ -z "$(ls -A /home/logs/archive 2>/dev/null)" ]; then
        echo "  → Removing empty /home/logs/archive/"
        rm -rf /home/logs/archive
    fi
fi

# Move archived logs if they contain useful data
if [ -d "/home/logs/archive" ] && [ -n "$(ls -A /home/logs/archive 2>/dev/null)" ]; then
    echo "  ℹ️  Keeping /home/logs/archive/ (contains useful data)"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ CLEANUP COMPLETE!                                     ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 FINAL REPOSITORY STRUCTURE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
tree -L 2 -d /home --gitignore -I 'hf_cache|models|LLaMA-Factory|__pycache__|*.egg-info'
echo ""
echo "🎯 ESSENTIAL FILES KEPT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ /configs/          - Training configurations (grammar, paraphrase, knowledge, comparison)"
echo "  ✅ /scripts/          - Working scripts (dataset prep, evaluation, training, monitoring)"
echo "  ✅ /data/             - Prepared datasets (JFLEG, PAWS, QQP, knowledge)"
echo "  ✅ /docs/             - Documentation"
echo "  ✅ /logs/             - Organized training logs"
echo "  ✅ /models/           - Fine-tuned model weights"
echo "  ✅ /LLaMA-Factory/    - Training framework"
echo "  ✅ /hf_cache/         - Hugging Face model cache"
echo "  ✅ README.md          - Main documentation"
echo "  ✅ QUICK_REFERENCE.txt - Quick command reference"
echo "  ✅ requirements.txt   - Python dependencies"
echo ""
echo "📁 DIRECTORY SIZES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
du -sh /home/configs /home/scripts /home/data /home/docs /home/logs 2>/dev/null || true
echo ""
echo "✅ Repository is now clean and ready for git commit!"
echo ""

