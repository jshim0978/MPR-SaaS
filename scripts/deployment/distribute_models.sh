#!/bin/bash
# Model Distribution Script - sbs29 → Production Nodes
# Generated: 2025-10-31
# Purpose: Transfer trained LoRA adapters to jw2, jw3, kcloud

set -e

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║           MODEL DISTRIBUTION: sbs29 → Production Nodes                    ║
╚═══════════════════════════════════════════════════════════════════════════╝

📦 MODELS TO DISTRIBUTE:
  → jw2 (129.254.202.252):   Cleaner (Grammar 3B + 8B)
  → jw3 (129.254.202.253):   Describer (Wikipedia-only 3B + 8B)  
  → kcloud (129.254.202.129): Paraphraser (PAWS+QQP 3B + 8B)

🔐 TRANSFER METHOD: rsync over SSH
⏱️  ESTIMATED TIME: 30-60 minutes

EOF

# Configuration
SOURCE_BASE="/home/models"
TARGET_BASE="/home/models"

# Node configurations
JW2_USER="etri"  # Change if different
JW2_IP="129.254.202.252"

JW3_USER="etri"
JW3_IP="129.254.202.253"

KCLOUD_USER="root"  # or appropriate user
KCLOUD_IP="129.254.202.129"

# Models to transfer (based on 3-worker architecture)
declare -A MODELS=(
    # Cleaner (Grammar) → jw2
    ["llama32_3b_grammar_lora"]="jw2"
    ["llama31_8b_grammar_lora"]="jw2"
    
    # Describer (Wikipedia-only) → jw3
    ["llama32_3b_wikipedia_only_lora"]="jw3"
    ["llama31_8b_wikipedia_only_lora"]="jw3"
    
    # Paraphraser (PAWS+QQP) → kcloud
    ["llama32_3b_paraphrase_lora"]="kcloud"
    ["llama31_8b_paraphrase_lora"]="kcloud"
)

# Function to get node connection string
get_node_conn() {
    case $1 in
        jw2) echo "${JW2_USER}@${JW2_IP}" ;;
        jw3) echo "${JW3_USER}@${JW3_IP}" ;;
        kcloud) echo "${KCLOUD_USER}@${KCLOUD_IP}" ;;
        *) echo "unknown" ;;
    esac
}

# Function to transfer model
transfer_model() {
    local model=$1
    local node=$2
    local conn=$(get_node_conn $node)
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Transferring: $model → $node ($conn)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Create target directory
    echo "1. Creating target directory..."
    ssh $conn "mkdir -p ${TARGET_BASE}/${model}"
    
    # Transfer model
    echo "2. Transferring files..."
    rsync -avz --progress \
        --exclude='training_args.bin' \
        --exclude='optimizer.pt' \
        --exclude='checkpoint-*' \
        ${SOURCE_BASE}/${model}/ \
        ${conn}:${TARGET_BASE}/${model}/
    
    # Verify
    echo "3. Verifying transfer..."
    ssh $conn "ls -lh ${TARGET_BASE}/${model}/ | head -10"
    
    echo "✅ Transfer complete: $model → $node"
    echo ""
}

# Main execution
echo "🚀 Starting model distribution..."
echo ""

# Check if source models exist
echo "Verifying source models..."
for model in "${!MODELS[@]}"; do
    if [ ! -d "${SOURCE_BASE}/${model}" ]; then
        echo "❌ ERROR: Model not found: ${SOURCE_BASE}/${model}"
        exit 1
    fi
done
echo "✅ All source models verified"
echo ""

# Test SSH connectivity
echo "Testing SSH connectivity..."
for node in jw2 jw3 kcloud; do
    conn=$(get_node_conn $node)
    echo -n "  Testing $node ($conn)... "
    if ssh -o ConnectTimeout=5 $conn "echo OK" &>/dev/null; then
        echo "✅"
    else
        echo "❌ FAILED"
        echo "ERROR: Cannot connect to $node"
        exit 1
    fi
done
echo ""

# Prompt for confirmation
read -p "Proceed with model distribution? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Distribution canceled."
    exit 0
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "TRANSFERRING MODELS..."
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Transfer each model
for model in "${!MODELS[@]}"; do
    node="${MODELS[$model]}"
    transfer_model "$model" "$node"
done

# Summary
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ MODEL DISTRIBUTION COMPLETE!"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 SUMMARY:"
echo "  → jw2:    Cleaner (Grammar 3B + 8B)"
echo "  → jw3:    Describer (Wikipedia-only 3B + 8B)"
echo "  → kcloud: Paraphraser (PAWS+QQP 3B + 8B)"
echo ""
echo "📝 Next steps:"
echo "  1. Pull latest code on all nodes (see git_sync_nodes.sh)"
echo "  2. Test model loading on each node"
echo "  3. Start framework implementation (Week 1 plan)"
echo ""

