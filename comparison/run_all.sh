#!/bin/bash
# Master Script to Run All Comparison Experiments
# This script orchestrates the complete evaluation pipeline

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║           MPR-SAAS COMPARISON EXPERIMENTS - MASTER RUNNER                ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
COMPARISON_DIR="/home/comparison"
RESULTS_DIR="$COMPARISON_DIR/results"
DATASETS_DIR="$COMPARISON_DIR/datasets"

# Check prerequisites
echo "🔍 Checking prerequisites..."
echo ""

# Check API keys (optional - will skip commercial baselines if not set)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set - GPT-4 baseline will be skipped"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set - Claude baseline will be skipped"
fi

# Check MPR-SaaS orchestrator
echo "🔍 Checking MPR-SaaS orchestrator..."
if curl -s http://129.254.202.251:8000/health > /dev/null 2>&1; then
    echo "✅ MPR-SaaS orchestrator is running"
else
    echo "⚠️  MPR-SaaS orchestrator not reachable - will skip MPR-SaaS baseline"
    echo "   Start workers (jw2, jw3, kcloud) and orchestrator (jw1) first"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 1: Dataset Preparation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$DATASETS_DIR"
if [ ! -f "hhem_500.json" ] || [ ! -f "truthfulqa_200.json" ] || [ ! -f "casual_200.json" ]; then
    echo "📊 Preparing datasets..."
    python3 prepare_datasets.py
else
    echo "✅ Datasets already prepared"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 2: Running Baselines on All Datasets"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run evaluation harness
cd "$COMPARISON_DIR/eval_harness"
python3 runner.py \
    --datasets hhem casual \
    --baselines control template cot mpr_saas \
    --output "$RESULTS_DIR" \
    --num-samples 50 \
    --verbose

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 3: Analysis & Visualization"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$COMPARISON_DIR/analysis"

echo "📊 Aggregating results..."
python3 aggregate.py --results-dir "$RESULTS_DIR"

echo "📈 Statistical significance tests..."
python3 significance.py --results-dir "$RESULTS_DIR"

echo "📉 Generating visualizations..."
python3 visualize.py --results-dir "$RESULTS_DIR"

echo "📄 Generating LaTeX tables..."
python3 latex_tables.py --results-dir "$RESULTS_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 4: Final Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 generate_report.py --results-dir "$RESULTS_DIR" --output "$RESULTS_DIR/COMPARISON_REPORT.md"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                         ✅ ALL EXPERIMENTS COMPLETE!                      ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results saved to: $RESULTS_DIR"
echo "📄 Final report: $RESULTS_DIR/COMPARISON_REPORT.md"
echo ""
echo "Key files:"
echo "  • $RESULTS_DIR/aggregated_metrics.csv"
echo "  • $RESULTS_DIR/significance_tests.txt"
echo "  • $RESULTS_DIR/plots/cost_vs_hhem.png"
echo "  • $RESULTS_DIR/plots/latency_distribution.png"
echo "  • $RESULTS_DIR/latex_tables.tex"
echo ""

