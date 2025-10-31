#!/bin/bash
# Git Sync Script - Pull latest code on all production nodes
# Generated: 2025-10-31

set -e

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║            GIT SYNC: Pull Latest Code on All Nodes                        ║
╚═══════════════════════════════════════════════════════════════════════════╝

🎯 TARGET NODES:
  → jw1 (129.254.202.251): Orchestrator
  → jw2 (129.254.202.252): Cleaner (Grammar)
  → jw3 (129.254.202.253): Describer (Wikipedia)
  → kcloud (129.254.202.129): Backup/Testing (Wiki+Wikidata)

📋 OPERATIONS:
  1. SSH to each node
  2. Navigate to /home
  3. Git pull latest changes
  4. Verify sync

EOF

# Node configurations
declare -A NODES=(
    ["jw1"]="etri@129.254.202.251"
    ["jw2"]="etri@129.254.202.252"
    ["jw3"]="etri@129.254.202.253"
    ["kcloud"]="root@129.254.202.129"
)

REPO_PATH="/home"
REPO_URL="https://github.com/jshim0978/MPR-SaaS.git"

# Function to sync node
sync_node() {
    local node=$1
    local conn=${NODES[$node]}
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔄 Syncing: $node ($conn)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    ssh $conn << ENDSSH
        cd ${REPO_PATH}
        
        # Initialize git if needed
        if [ ! -d ".git" ]; then
            echo "  ⚠️  Git not initialized, cloning repository..."
            git clone ${REPO_URL} temp_clone
            rsync -a temp_clone/ ./
            rm -rf temp_clone
        fi
        
        # Stash any local changes
        if ! git diff --quiet; then
            echo "  📦 Stashing local changes..."
            git stash
        fi
        
        # Pull latest
        echo "  ⬇️  Pulling latest changes..."
        git pull origin master || git pull origin main
        
        # Show current commit
        echo "  📍 Current commit:"
        git log -1 --oneline
        
        echo "  ✅ Sync complete: $node"
ENDSSH
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully synced: $node"
    else
        echo "❌ Failed to sync: $node"
        return 1
    fi
    echo ""
}

# Main execution
echo "🚀 Starting git sync across all nodes..."
echo ""

# Test connectivity first
echo "Testing SSH connectivity..."
failed_nodes=()
for node in "${!NODES[@]}"; do
    conn=${NODES[$node]}
    echo -n "  Testing $node ($conn)... "
    if ssh -o ConnectTimeout=5 $conn "echo OK" &>/dev/null; then
        echo "✅"
    else
        echo "❌ FAILED"
        failed_nodes+=("$node")
    fi
done

if [ ${#failed_nodes[@]} -ne 0 ]; then
    echo ""
    echo "⚠️  WARNING: Cannot connect to: ${failed_nodes[*]}"
    echo "These nodes will be skipped."
    echo ""
fi

# Prompt for confirmation
read -p "Proceed with git sync? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Sync canceled."
    exit 0
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "SYNCING NODES..."
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Sync each node
success_count=0
for node in "${!NODES[@]}"; do
    # Skip if connectivity test failed
    if [[ " ${failed_nodes[@]} " =~ " ${node} " ]]; then
        echo "⏭️  Skipping $node (no connectivity)"
        continue
    fi
    
    if sync_node "$node"; then
        ((success_count++))
    fi
done

# Summary
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ GIT SYNC COMPLETE!"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 SUMMARY:"
echo "  Total nodes: ${#NODES[@]}"
echo "  Successfully synced: $success_count"
echo "  Failed: $((${#NODES[@]} - success_count))"
echo ""
echo "📝 Next steps:"
echo "  1. Verify models are in place on each node"
echo "  2. Test model loading"
echo "  3. Start service implementation (Week 1 Day 1)"
echo ""

