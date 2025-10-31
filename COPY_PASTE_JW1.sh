#!/bin/bash
# COMPLETE JW1 SETUP - Copy and paste this entire script
# Run as: bash -c "$(cat << 'ENDOFSCRIPT'
# ... paste everything below ...
# ENDOFSCRIPT
# )"

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║                    JW1: ORCHESTRATOR COMPLETE SETUP                       ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF

set -e

# Step 1: Setup Git (no credentials needed for public repo)
echo "📥 STEP 1: Setting up Git..."
cd /home

if ! command -v git &> /dev/null; then
    echo "Installing git..."
    sudo yum install -y git || sudo apt-get install -y git
fi

# Step 2: Clone repository (public, no auth needed)
echo "📥 STEP 2: Cloning code from GitHub..."
if [ -d ".git" ]; then
    echo "Repository exists, pulling latest..."
    git pull origin main || git fetch origin && git reset --hard origin/main
else
    echo "Cloning repository..."
    git clone https://github.com/jshim0978/MPR-SaaS.git temp
    rsync -av temp/ ./
    rm -rf temp
    cd /home
fi

# Step 3: Setup Python environment
echo "📦 STEP 3: Setting up Python environment..."

# Install pip if not present
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    sudo yum install -y python3-pip || sudo apt-get install -y python3-pip
fi

# Install dependencies
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt --user
fi

# Step 4: Verify installation
echo "✅ STEP 4: Verifying installation..."
ls -la /home/orchestrator/
ls -la /home/mpr/

cat << 'COMPLETE'

═══════════════════════════════════════════════════════════════════════════
✅ JW1 SETUP COMPLETE!
═══════════════════════════════════════════════════════════════════════════

📋 Status:
  ✓ Code cloned from GitHub
  ✓ Dependencies installed
  ✓ No models needed (orchestrator only)

🚀 TO START SERVICE (after jw2, jw3, kcloud are running):

   cd /home/orchestrator
   python3 app.py

Expected output:
  🎯 Orchestrator Starting...
  🔗 Cleaner:      http://129.254.202.252:8002
  🔗 Describer:    http://129.254.202.253:8003
  🔗 Paraphraser:  http://129.254.202.129:8004
  🌐 Listening on: 0.0.0.0:8000

🧪 TO TEST (after starting):
   curl http://localhost:8000/health

COMPLETE

echo ""
echo "✅ All done! JW1 is ready."

