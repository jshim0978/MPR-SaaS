# Git Push and Pull Workflow Guide

## Step 1: Push from Training Server (sbs29)

### Option A: If you have a git repository URL already
```bash
cd /home

# Add remote (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/praas-mpr.git
# OR if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/praas-mpr.git

# Push to remote
git push -u origin master

# Verify push
git remote -v
git log --oneline | head -3
```

### Option B: If you need to create a new repository
1. Go to GitHub/GitLab/Bitbucket
2. Create new repository (e.g., "praas-mpr" or "mpr-agents")
3. Copy the repository URL
4. Run commands from Option A above

---

## Step 2: Pull on Each Production Node

Once Step 1 is complete, you can pull on each node:

### jw1 (Master/Gateway) - 129.254.202.251
```bash
ssh etri@129.254.202.251

cd /home

# If git is not initialized yet:
git clone <YOUR_REPO_URL> temp_repo
rsync -av temp_repo/ ./
rm -rf temp_repo

# OR if git is already initialized:
git remote add origin <YOUR_REPO_URL>
git pull origin master

# Verify
git log -1
ls configs/ scripts/
```

### jw2 (Cleaner) - 129.254.202.252
```bash
ssh etri@129.254.202.252

cd /home

# Clone or pull (same as jw1)
git clone <YOUR_REPO_URL> temp_repo
rsync -av temp_repo/ ./
rm -rf temp_repo

# Verify
git log -1
# Models will be added separately via rsync
```

### jw3 (Describer) - 129.254.202.253
```bash
ssh etri@129.254.202.253

cd /home

# Clone or pull (same as jw1)
git clone <YOUR_REPO_URL> temp_repo
rsync -av temp_repo/ ./
rm -rf temp_repo

# Verify
git log -1
```

### kcloud (Paraphraser) - 129.254.202.129
```bash
ssh root@129.254.202.129

cd /home

# Clone or pull (same as jw1)
git clone <YOUR_REPO_URL> temp_repo
rsync -av temp_repo/ ./
rm -rf temp_repo

# Verify
git log -1
```

---

## Automated Version: Use git_sync_nodes.sh

After you push from training server, you can use the automated script:

```bash
# Edit the script to add your repo URL:
nano /home/scripts/deployment/git_sync_nodes.sh
# Update line: REPO_URL="YOUR_GIT_REPO_URL_HERE"

# Then run:
/home/scripts/deployment/git_sync_nodes.sh
```

This will automatically:
1. Clone/pull on all 4 nodes
2. Verify sync
3. Report status

---

## Important Notes

### ✅ What Gets Synced via Git:
- configs/
- scripts/
- docs/
- README.md, requirements.txt
- All code files

### ❌ What Does NOT Get Synced (separate distribution):
- models/ (too large for git)
- data/ (too large)
- logs/
- hf_cache/

**Models must be distributed separately using:**
```bash
/home/scripts/deployment/distribute_models.sh
```

---

## Complete Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│ Training Server (sbs29)                                     │
│ ─────────────────────────────────────────────────────────── │
│ 1. git push origin master              [Push code to git]  │
│ 2. ./distribute_models.sh              [Send models via rsync] │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─── git pull ───→ jw1  (code only)
                            ├─── git pull ───→ jw2  (code only)
                            ├─── git pull ───→ jw3  (code only)
                            └─── git pull ───→ kcloud (code only)
                            
                            │
                            ├─── rsync models ───→ jw2  (Cleaner models)
                            ├─── rsync models ───→ jw3  (Describer models)
                            └─── rsync models ───→ kcloud (Paraphraser models)
```

---

## Quick Commands Reference

### On Training Server (sbs29):
```bash
# 1. Push code
cd /home
git remote add origin <URL>
git push -u origin master

# 2. Distribute models
/home/scripts/deployment/distribute_models.sh
```

### On Each Production Node:
```bash
# Pull code
cd /home
git clone <URL> temp && rsync -av temp/ ./ && rm -rf temp

# Verify
git log -1
ls configs/ scripts/

# Models will arrive via rsync from sbs29
```

---

## Troubleshooting

### If git push fails:
```bash
# Check if remote is set correctly
git remote -v

# If wrong, remove and re-add
git remote remove origin
git remote add origin <CORRECT_URL>
git push -u origin master
```

### If git pull fails on nodes:
```bash
# Force fresh clone
cd /home
rm -rf .git
git clone <URL> temp
rsync -av temp/ ./
rm -rf temp
```

### If SSH keys needed:
```bash
# Generate SSH key on each node
ssh-keygen -t ed25519 -C "node@etri.re.kr"

# Add to GitHub/GitLab
cat ~/.ssh/id_ed25519.pub
# Copy and add to repository settings
```

---

**Status:** Ready to push to repository!
**Next:** Provide your git repository URL to complete Step 1

