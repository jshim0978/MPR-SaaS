#!/bin/bash
# JW1 DEPLOYMENT SCRIPT - Orchestrator
# IP: 129.254.202.251
# User: etri
# Role: Orchestrates 3 workers (Cleaner, Describer, Paraphraser)

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║                    JW1: ORCHESTRATOR DEPLOYMENT                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF

# Step 1: Clone code
echo "📥 STEP 1: Pulling code from GitHub..."
cd /home
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/jshim0978/MPR-SaaS.git temp
    rsync -av temp/ ./
    rm -rf temp
fi

# Step 2: Install dependencies
echo "📦 STEP 2: Installing dependencies..."
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt --user
fi

# Step 3: Verify
echo "✅ STEP 3: Verifying installation..."
ls -la /home/orchestrator/
ls -la /home/mpr/

cat << 'EOF'

═══════════════════════════════════════════════════════════════════════════
✅ JW1 SETUP COMPLETE!
═══════════════════════════════════════════════════════════════════════════

📋 No models needed on jw1 (orchestrator only)

🚀 TO START SERVICE (after jw2, jw3, kcloud are running):
   cd /home/orchestrator
   python3 app.py

Expected output:
  🎯 Orchestrator Starting...
  🔗 Cleaner:      http://129.254.202.252:8002
  🔗 Describer:    http://129.254.202.253:8003
  🔗 Paraphraser:  http://129.254.202.129:8004
  🌐 Listening on: 0.0.0.0:8000

EOF

