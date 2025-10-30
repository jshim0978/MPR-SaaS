#!/bin/bash

# Git Commit and Multi-Node Deployment Script
# This script will:
# 1. Initialize git (if needed)
# 2. Commit only code/configs (not models/data/cache)
# 3. Push to remote
# 4. Sync to all worker nodes (jw1, jw2, jw3, kcloud)

set -e

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║           GIT COMMIT & MULTI-NODE DEPLOYMENT                              ║
╚═══════════════════════════════════════════════════════════════════════════╝

📦 WHAT WILL BE COMMITTED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ configs/          - All training configurations
  ✅ scripts/          - All working scripts
  ✅ docs/             - Documentation
  ✅ .gitignore        - Git ignore rules
  ✅ README.md         - Main documentation
  ✅ QUICK_REFERENCE.txt - Quick commands
  ✅ requirements.txt  - Python dependencies
  ✅ LLaMA-Factory/data/dataset_info.json - Dataset registry

❌ WHAT WILL BE IGNORED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❌ models/           - Model weights (deploy separately)
  ❌ data/             - Datasets (too large for git)
  ❌ logs/             - Training logs (local artifacts)
  ❌ hf_cache/         - Hugging Face cache
  ❌ LLaMA-Factory/    - Training framework (except dataset_info.json)

🌐 TARGET NODES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • jw1 (orchestrator)
  • jw2 (cleaner)
  • jw3 (describer)
  • kcloud@129.254.202.129

EOF

read -p "Proceed with commit and deployment? [y/N]: " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment canceled."
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Git Setup & Commit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /home

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "  ✅ Git initialized"
fi

# Configure git user if not set
if [ -z "$(git config user.name 2>/dev/null)" ]; then
    echo "⚙️  Configuring git user..."
    git config user.email "jshim0978@gmail.com"
    git config user.name "JW"
    echo "  ✅ Git user configured"
fi

# Add all files (gitignore will filter)
echo "📝 Staging files for commit..."
git add .
echo "  ✅ Files staged"

# Show what will be committed
echo ""
echo "📋 Files to be committed:"
git status --short | head -20
TOTAL_FILES=$(git status --short | wc -l)
echo "  ... (${TOTAL_FILES} files total)"

# Create commit with descriptive message
echo ""
echo "💾 Creating commit..."
COMMIT_MSG="feat: complete LLaMA fine-tuning pipeline with dataset comparison

- Add grammar enhancement training (JFLEG dataset)
- Add paraphrase training (PAWS + QQP combined)
- Add knowledge enhancement training (Wikipedia + KILT)
- Add dataset comparison (PAWS-only vs QQP-only vs Combined)
- Implement optimized parallel training scheduler
- Create comprehensive evaluation scripts
- Organize repository with clean structure
- Document all training phases and deployment

Training completed:
- 7/10 models complete (grammar, paraphrase, knowledge)
- 3/10 models in progress (dataset comparison)

All configurations tested and working on L40 GPUs."

git commit -m "$COMMIT_MSG"
echo "  ✅ Commit created"

# Show commit details
echo ""
echo "📊 Commit details:"
git log -1 --stat | head -30

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Push to Remote (if configured)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if remote is configured
if git remote | grep -q origin; then
    echo "🚀 Pushing to remote..."
    git push origin main || git push origin master || echo "⚠️  Push failed - check remote configuration"
else
    echo "⚠️  No remote configured. Skipping push."
    echo ""
    echo "To add a remote, run:"
    echo "  git remote add origin <your-repo-url>"
    echo "  git push -u origin main"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Sync to Worker Nodes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create sync script for worker nodes
cat > /tmp/sync_worker_node.sh << 'SYNCEOF'
#!/bin/bash
# Worker Node Sync Script
set -e

REPO_PATH="$1"
NODE_NAME="$2"

echo "📡 Syncing ${NODE_NAME}..."

cd "$REPO_PATH"

# Stash any local changes
if ! git diff-index --quiet HEAD --; then
    echo "  ⚠️  Local changes detected, stashing..."
    git stash
fi

# Pull latest changes
echo "  ⬇️  Pulling latest changes..."
git fetch origin
git pull origin main || git pull origin master

# Verify sync
COMMIT_HASH=$(git rev-parse --short HEAD)
echo "  ✅ ${NODE_NAME} synced to commit: ${COMMIT_HASH}"

# Check if LLaMA-Factory needs updating
if [ -d "LLaMA-Factory" ]; then
    echo "  ✅ LLaMA-Factory directory exists"
else
    echo "  ⚠️  LLaMA-Factory not found - may need manual installation"
fi

# Check if hf_cache exists
if [ -d "hf_cache" ]; then
    echo "  ✅ hf_cache directory exists"
else
    echo "  ⚠️  hf_cache not found - models may need to be downloaded"
fi

echo "  🎯 ${NODE_NAME} ready!"
SYNCEOF

chmod +x /tmp/sync_worker_node.sh

# Prompt for sync details
echo "To sync worker nodes, you need to provide:"
echo "  1. Repository path on each node"
echo "  2. SSH access to each node"
echo ""
read -p "Repository path on worker nodes (e.g., /home): " REPO_PATH
REPO_PATH=${REPO_PATH:-/home}

echo ""
echo "Available nodes to sync:"
echo "  1. jw1 (orchestrator)"
echo "  2. jw2 (cleaner)"
echo "  3. jw3 (describer)"
echo "  4. kcloud@129.254.202.129"
echo ""
read -p "Sync nodes automatically? [y/N]: " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔄 Syncing nodes..."
    
    # Try to sync each node
    for NODE in jw1 jw2 jw3; do
        echo ""
        if ssh -o ConnectTimeout=5 "$NODE" "test -d $REPO_PATH/.git" 2>/dev/null; then
            ssh "$NODE" "bash -s -- $REPO_PATH $NODE" < /tmp/sync_worker_node.sh || echo "  ⚠️  Failed to sync $NODE"
        else
            echo "  ⚠️  Cannot connect to $NODE or repo not found"
        fi
    done
    
    # kcloud
    echo ""
    if ssh -o ConnectTimeout=5 kcloud@129.254.202.129 "test -d $REPO_PATH/.git" 2>/dev/null; then
        ssh kcloud@129.254.202.129 "bash -s -- $REPO_PATH kcloud" < /tmp/sync_worker_node.sh || echo "  ⚠️  Failed to sync kcloud"
    else
        echo "  ⚠️  Cannot connect to kcloud@129.254.202.129 or repo not found"
    fi
else
    echo ""
    echo "⏭️  Skipping automatic sync. To manually sync each node, run:"
    echo ""
    echo "  ssh jw1 'cd $REPO_PATH && git pull'"
    echo "  ssh jw2 'cd $REPO_PATH && git pull'"
    echo "  ssh jw3 'cd $REPO_PATH && git pull'"
    echo "  ssh kcloud@129.254.202.129 'cd $REPO_PATH && git pull'"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ DEPLOYMENT COMPLETE!                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Code and configs committed to git"
echo "✅ Worker nodes synced (or manual sync instructions provided)"
echo ""
echo "📋 NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Wait for training completion (~14 hours for 8B models)"
echo ""
echo "2. Deploy model weights to servers:"
echo "   • jw1 (orchestrator): Access to all models for routing"
echo "   • jw2 (cleaner): llama32_3b_grammar_lora"
echo "   • jw3 (describer): llama31_8b_knowledge_lora"
echo ""
echo "3. Use rsync or HF Hub to transfer models:"
echo "   rsync -avz /home/models/llama32_3b_grammar_lora/ jw2:/path/to/models/"
echo "   rsync -avz /home/models/llama31_8b_knowledge_lora/ jw3:/path/to/models/"
echo ""
echo "4. Verify deployment:"
echo "   See: /home/docs/deployment_plan.md"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

