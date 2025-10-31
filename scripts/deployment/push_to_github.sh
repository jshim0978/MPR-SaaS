#!/bin/bash
# Quick Git Push Script with Manual Credential Entry
# Run this script to push to GitHub

cd /home

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║                    PUSH TO GITHUB REPOSITORY                              ║
╚═══════════════════════════════════════════════════════════════════════════╝

Repository: https://github.com/jshim0978/MPR-SaaS

📋 OPTIONS TO PUSH:

Option 1: Use GitHub Personal Access Token (Recommended)
─────────────────────────────────────────────────────────
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: repo (all)
4. Copy the token
5. Run this:

   git push -u origin main

   Username: jshim0978
   Password: <paste your token>

Option 2: Use SSH (One-time setup)
───────────────────────────────────
1. Generate SSH key:
   ssh-keygen -t ed25519 -C "jshim0978@gmail.com"

2. Add to GitHub:
   cat ~/.ssh/id_ed25519.pub
   Copy and add to: https://github.com/settings/keys

3. Change remote to SSH:
   git remote set-url origin git@github.com:jshim0978/MPR-SaaS.git
   git push -u origin main

Option 3: Manual HTTPS Push
────────────────────────────
   GIT_ASKPASS=true git push -u origin main
   (Enter credentials when prompted)

EOF

read -p "Press Enter to attempt push with credential prompt..."

echo ""
echo "Attempting to push..."
echo "Enter your GitHub username and Personal Access Token when prompted."
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "   Repository: https://github.com/jshim0978/MPR-SaaS"
else
    echo ""
    echo "❌ Push failed. Please use one of the options above."
fi

