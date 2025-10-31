#!/bin/bash
# ADD WORKER SSH KEYS TO SBS29
# Run this script on sbs29 (training server) to add worker node SSH keys

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║           ADD WORKER NODE SSH KEYS TO SBS29                               ║
╚═══════════════════════════════════════════════════════════════════════════╝

This script helps you add SSH public keys from worker nodes (jw2, jw3, kcloud)
so they can access sbs29 to transfer models.

PROCESS:
1. Run deployment script on each worker node
2. Script will generate SSH key and show public key
3. Copy the public key
4. Add it here (or manually to ~/.ssh/authorized_keys)

EOF

# Ensure authorized_keys exists with correct permissions
mkdir -p ~/.ssh
touch ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

echo "Current SSH keys authorized on sbs29:"
echo "════════════════════════════════════════════════════════════════"
if [ -s ~/.ssh/authorized_keys ]; then
    cat -n ~/.ssh/authorized_keys
else
    echo "(none yet)"
fi
echo "════════════════════════════════════════════════════════════════"
echo ""

# Function to add a key
add_key() {
    local node_name=$1
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "ADD SSH KEY FOR: $node_name"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Paste the SSH public key (starts with 'ssh-ed25519 ...'):"
    echo "Then press Enter twice to confirm."
    echo ""
    read -r pubkey
    
    if [ -z "$pubkey" ]; then
        echo "⚠️  No key provided, skipping..."
        return
    fi
    
    # Check if key already exists
    if grep -qF "$pubkey" ~/.ssh/authorized_keys 2>/dev/null; then
        echo "ℹ️  Key already exists in authorized_keys"
        return
    fi
    
    # Add key with comment
    echo "$pubkey # $node_name-$(date +%Y%m%d)" >> ~/.ssh/authorized_keys
    echo "✅ Key added for $node_name"
}

# Add keys for each worker
echo "Let's add SSH keys for each worker node."
echo ""
echo "For each node:"
echo "1. Run the COPY_PASTE_<node>.sh script"
echo "2. When it shows the SSH public key, copy it"
echo "3. Come back here and paste it"
echo ""

read -p "Ready to add JW2 (Cleaner) SSH key? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    add_key "jw2-cleaner"
fi

read -p "Ready to add JW3 (Describer) SSH key? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    add_key "jw3-describer"
fi

read -p "Ready to add KCLOUD (Paraphraser) SSH key? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    add_key "kcloud-paraphraser"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "FINAL authorized_keys:"
echo "═══════════════════════════════════════════════════════════════"
cat -n ~/.ssh/authorized_keys

echo ""
echo "✅ SSH key setup complete!"
echo ""
echo "Now return to each worker node and press Enter to continue their setup."
echo ""

