# 3-Worker Deployment: Easy Copy-Paste Guide

**Architecture**: Orchestrator + 3 Specialist Workers  
**Date**: October 31, 2025  
**Status**: Ready for deployment  

---

## 🏗️ System Architecture

```
User Prompt → jw1 (Orchestrator :8000)
              ↓
              Parallel Fan-Out to 3 Workers:
              ├─→ jw2 (Cleaner      :8002) Fix typos/grammar
              ├─→ jw3 (Describer    :8003) Add Wikipedia context
              └─→ kcloud (Paraphraser :8004) Rephrase for clarity
              ↓
              Merger: Combine all improvements
              ↓
              Refined Prompt → Target LLM
```

---

## 📦 Node Configuration

| Node | IP | User | Role | Models | Port |
|------|-----|------|------|--------|------|
| **jw1** | 129.254.202.251 | etri | Orchestrator | None | 8000 |
| **jw2** | 129.254.202.252 | etri | Cleaner | Grammar 3B+8B | 8002 |
| **jw3** | 129.254.202.253 | etri | Describer | Wikipedia 3B+8B (8.8/10) | 8003 |
| **kcloud** | 129.254.202.129 | root | Paraphraser | PAWS+QQP 3B+8B | 8004 |

---

## 🚀 One-Command Deployment Per Node

### Step 1: On JW1 (Orchestrator)

```bash
ssh etri@129.254.202.251
curl -sSL https://raw.githubusercontent.com/jshim0978/MPR-SaaS/main/scripts/deployment/deploy_jw1.sh | bash
```

**Or manually:**
```bash
ssh etri@129.254.202.251
cd /home
git clone https://github.com/jshim0978/MPR-SaaS.git temp && rsync -av temp/ ./ && rm -rf temp
pip3 install -r requirements.txt --user
cd /home/orchestrator
python3 app.py
```

### Step 2: On JW2 (Cleaner)

```bash
ssh etri@129.254.202.252
/home/scripts/deployment/deploy_jw2.sh
# (after code is pulled)
```

**What it does:**
1. Pulls code from GitHub
2. Installs dependencies
3. Transfers Grammar models (3B + 8B) from sbs29
4. Downloads base Llama models
5. Tests model loading
6. Ready to start: `cd /home/workers/cleaner && python3 app.py`

### Step 3: On JW3 (Describer)

```bash
ssh etri@129.254.202.253
/home/scripts/deployment/deploy_jw3.sh
# (after code is pulled)
```

**What it does:**
1. Pulls code from GitHub
2. Installs dependencies
3. Transfers Wikipedia models (3B + 8B) from sbs29
4. Downloads base Llama models
5. Tests model loading
6. Ready to start: `cd /home/workers/descr && python3 app.py`

### Step 4: On KCLOUD (Paraphraser)

```bash
ssh root@129.254.202.129
/home/scripts/deployment/deploy_kcloud.sh
# (after code is pulled)
```

**What it does:**
1. Pulls code from GitHub
2. Installs dependencies
3. Transfers Paraphrase models (3B + 8B) from sbs29
4. Downloads base Llama models
5. Tests model loading
6. Ready to start: `cd /home/workers/paraphraser && python3 app.py`

---

## 🎯 Startup Order

**1. Start Workers First (any order):**
```bash
# On jw2:
cd /home/workers/cleaner && python3 app.py

# On jw3:
cd /home/workers/descr && python3 app.py

# On kcloud:
cd /home/workers/paraphraser && python3 app.py
```

**2. Start Orchestrator Last:**
```bash
# On jw1 (after all workers are running):
cd /home/orchestrator && python3 app.py
```

---

## ✅ Verification

### Health Checks
```bash
curl http://129.254.202.252:8002/health  # Cleaner
curl http://129.254.202.253:8003/health  # Describer
curl http://129.254.202.129:8004/health  # Paraphraser
curl http://129.254.202.251:8000/health  # Orchestrator
```

### End-to-End Test
```bash
curl -X POST http://129.254.202.251:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what is the captial of frane?"}'
```

**Expected Result:**
```json
{
  "skipped": false,
  "cleaned": {"cleaned": "what is the capital of France?"},
  "described": {"description": "France is a country in Western Europe..."},
  "paraphrased": {"paraphrased": "What is the capital city of France?"},
  "final_prompt": "What is the capital city of France?\n\nContext: France is...",
  "latency_ms": {"cleaner": 150, "descr": 180, "para": 140, "total": 200}
}
```

---

## 📊 Model Details

### Cleaner (jw2)
- **Training**: JFLEG (6,012 grammar correction samples)
- **Purpose**: Fix typos, grammar errors
- **Size**: 3B (~250MB) + 8B (~500MB)

### Describer (jw3)
- **Training**: Wikipedia-only (14,982 encyclopedic articles)
- **Purpose**: Add factual context and background
- **Quality**: 8.8/10 (best evaluated model)
- **Size**: 3B (~250MB) + 8B (~500MB)

### Paraphraser (kcloud)
- **Training**: PAWS + QQP (143,658 paraphrase pairs)
- **Purpose**: Rephrase for clarity and fluency
- **Size**: 3B (~250MB) + 8B (~500MB)

---

## 🔧 Troubleshooting

### "rsync: failed to connect"
- **Issue**: Can't reach sbs29 from worker node
- **Fix**: Check network connectivity, ensure sbs29 is accessible

### "No module named 'transformers'"
- **Issue**: Dependencies not installed
- **Fix**: `pip3 install -r requirements.txt --user`

### "Worker not responding"
- **Issue**: Worker service not started or crashed
- **Fix**: Check logs, restart service, ensure models loaded correctly

### "Port already in use"
- **Issue**: Service already running
- **Fix**: `pkill -f "python3 app.py"` then restart

---

## 📝 Manual Deployment Guide

If automated scripts don't work, see: `/home/MANUAL_DEPLOYMENT.sh`

---

**Status**: ✅ Ready for deployment  
**Repository**: https://github.com/jshim0978/MPR-SaaS  
**Last Updated**: October 31, 2025

