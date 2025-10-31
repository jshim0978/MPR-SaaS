# How to Get SSH Keys from Each Node

## 🔑 The Keys Are Generated Automatically!

You **don't need to get keys manually** - the deployment scripts generate them and show them to you!

---

## 📋 Step-by-Step Process

### STEP 1: Run Deployment Script on Worker Node

```bash
# Example: On JW2
ssh etri@129.254.202.252

# Copy and paste entire content of COPY_PASTE_JW2.sh
bash
```

### STEP 2: Script Auto-Generates Key

The script will:
1. Check if `~/.ssh/id_ed25519` exists
2. If not, run: `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "jw2-cleaner"`
3. **Display the public key on screen**

### STEP 3: Script Shows You The Key

You'll see output like this:

```
═══════════════════════════════════════════════════════════════════════
STEP 1: Setup SSH access to sbs29 (training server)
═══════════════════════════════════════════════════════════════════════
Generating SSH key...
✅ SSH key generated

📋 YOUR SSH PUBLIC KEY (add this to sbs29's ~/.ssh/authorized_keys):
════════════════════════════════════════════════════════════════════
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAbCdEfGhIjKlMnOpQrStUvWxYz... jw2-cleaner
════════════════════════════════════════════════════════════════════

⚠️  ACTION REQUIRED:
   1. Copy the key above
   2. On sbs29, run: echo '<YOUR_KEY>' >> ~/.ssh/authorized_keys
   3. Press Enter here when done...
```

### STEP 4: Copy The Key

**Just select and copy** the line starting with `ssh-ed25519`

### STEP 5: Add to SBS29

On sbs29, either:

**Option A - Use the helper script:**
```bash
bash /home/SBS29_ADD_WORKER_KEYS.sh
# Then paste the key when prompted
```

**Option B - Manual:**
```bash
echo 'ssh-ed25519 AAAAC3NzaC... jw2-cleaner' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### STEP 6: Continue on Worker

Go back to worker terminal and **press Enter**

Script will:
- Test SSH connection
- If successful: Continue with model transfer
- If failed: Show error and instructions

---

## 🔍 If You Need to Get an Existing Key

If a key was already generated but you need to see it again:

```bash
# On the worker node (jw2, jw3, or kcloud):
cat ~/.ssh/id_ed25519.pub
```

This shows the public key you need to add to sbs29.

---

## 🎯 Complete Workflow Example

### Terminal 1: JW2 (Worker)
```bash
ssh etri@129.254.202.252

# Paste COPY_PASTE_JW2.sh content
bash
```

**Output shows:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAbCdE... jw2-cleaner
```

**➡️ Copy this!**

### Terminal 2: SBS29 (Training Server)
```bash
# Run helper script
bash /home/SBS29_ADD_WORKER_KEYS.sh

# When prompted for jw2 key, paste:
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAbCdE... jw2-cleaner

# Press Enter
```

**Output:**
```
✅ Key added for jw2-cleaner
```

### Back to Terminal 1: JW2
```
Press Enter to continue...
```

**Output:**
```
Testing SSH connection to sbs29...
✅ SSH connection successful
```

Script continues with model transfer!

---

## 🔄 For All 3 Workers

Repeat the process for:
1. **JW2** (Cleaner)
2. **JW3** (Describer)  
3. **KCLOUD** (Paraphraser)

Each will generate its own unique key.

---

## 💡 Pro Tip: Parallel Setup

Open **4 terminals**:
- Terminal 1: sbs29 (running `SBS29_ADD_WORKER_KEYS.sh`)
- Terminal 2: jw2 (running `COPY_PASTE_JW2.sh`)
- Terminal 3: jw3 (running `COPY_PASTE_JW3.sh`)
- Terminal 4: kcloud (running `COPY_PASTE_KCLOUD.sh`)

As each worker shows its key:
1. Copy key from worker terminal
2. Switch to sbs29 terminal
3. Paste key
4. Switch back to worker terminal
5. Press Enter

All workers will then transfer models **in parallel**!

---

## 🐛 Troubleshooting

### "Key already exists"

The script checks for existing keys. If found, it shows:
```
SSH key already exists at ~/.ssh/id_ed25519
```

To see the existing key:
```bash
cat ~/.ssh/id_ed25519.pub
```

### "Permission denied after adding key"

Check on sbs29:
```bash
# Verify key is there
grep "jw2-cleaner" ~/.ssh/authorized_keys

# Fix permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### "Can't reach sbs29"

Test network connectivity:
```bash
ping 129.254.202.29
```

---

## ✅ Summary

**You DON'T manually get keys from nodes.**

**The deployment scripts:**
1. ✅ Generate keys automatically
2. ✅ Display them on screen for you
3. ✅ Wait for you to add them to sbs29
4. ✅ Test the connection
5. ✅ Continue with setup

**Just copy-paste what you see on screen!**

