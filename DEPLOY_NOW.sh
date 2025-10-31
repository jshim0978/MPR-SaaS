#!/bin/bash
# Quick Start: Deploy PRaaS/MPR-SaaS from Training Server
# Run this on sbs29 (129.254.202.29)

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║             PRaaS/MPR-SaaS DEPLOYMENT - QUICK START                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

📍 Current Node: sbs29 (Training Server)
🎯 Target Nodes: jw1, jw2, jw3, kcloud

═══════════════════════════════════════════════════════════════════════════
STEP 1: SYNC CODE TO ALL NODES
═══════════════════════════════════════════════════════════════════════════

EOF

read -p "Press Enter to sync code to jw1, jw2, jw3, kcloud..."

echo ""
echo "🚀 Syncing code from GitHub to all nodes..."
/home/scripts/deployment/git_sync_nodes.sh

if [ $? -ne 0 ]; then
    echo "❌ Code sync failed. Check errors above."
    exit 1
fi

cat << 'EOF'

═══════════════════════════════════════════════════════════════════════════
STEP 2: DISTRIBUTE TRAINED MODELS
═══════════════════════════════════════════════════════════════════════════

Models to distribute:
  • jw2:    Grammar Cleaner (3B + 8B)
  • jw3:    Wikipedia Describer (3B + 8B)
  • kcloud: Wiki+Wikidata Backup (3B + 8B)

Estimated time: 30-60 minutes

EOF

read -p "Press Enter to start model distribution..."

echo ""
echo "📦 Distributing models to nodes..."
/home/scripts/deployment/distribute_models.sh

if [ $? -ne 0 ]; then
    echo "❌ Model distribution failed. Check errors above."
    exit 1
fi

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║                    ✅ DEPLOYMENT COMPLETE                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

📋 NEXT STEPS - Follow Instructions Per Node:

📖 Full guide: /home/DEPLOYMENT_INSTRUCTIONS.md

───────────────────────────────────────────────────────────────────────────
ON EACH NODE:
───────────────────────────────────────────────────────────────────────────

1️⃣  jw2 (Cleaner Worker)
   ssh etri@129.254.202.252
   
   • Verify models: ls -lh /home/models/llama*grammar*
   • Download base models (Llama 3B + 8B)
   • Test model loading
   • Start: cd /home/workers/cleaner && python3 app.py

2️⃣  jw3 (Describer Worker)  
   ssh etri@129.254.202.253
   
   • Verify models: ls -lh /home/models/llama*wikipedia*
   • Download base models (Llama 3B + 8B)
   • Test model loading
   • Start: cd /home/workers/descr && python3 app.py

3️⃣  jw1 (Orchestrator)
   ssh etri@129.254.202.251
   
   • Verify code: ls -la /home/orchestrator/
   • Wait for jw2 and jw3 to be running
   • Test worker health checks
   • Start: cd /home/orchestrator && python3 app.py

4️⃣  kcloud (Backup/Testing)
   ssh root@129.254.202.129
   
   • Verify models: ls -lh /home/models/llama*knowledge*
   • Keep for testing and backup

───────────────────────────────────────────────────────────────────────────
VERIFICATION:
───────────────────────────────────────────────────────────────────────────

After all services running, test end-to-end from jw1:

   curl http://129.254.202.251:8000/health  # Orchestrator
   curl http://129.254.202.252:8002/health  # Cleaner
   curl http://129.254.202.253:8003/health  # Describer

   # Full test
   curl -X POST http://129.254.202.251:8000/refine \
     -H "Content-Type: application/json" \
     -d '{"prompt": "what is the captial of frane?", "run_id": "test-001"}'

───────────────────────────────────────────────────────────────────────────

📖 Detailed per-node instructions: /home/DEPLOYMENT_INSTRUCTIONS.md
📊 Model selection rationale: /home/docs/FINAL_MODEL_SELECTION.md
🔧 Architecture rules: /home/.cursor/rules/eacl-manuscript-rules.mdc

EOF

echo ""
echo "Deployment from sbs29 complete! Follow per-node instructions above."
echo ""

