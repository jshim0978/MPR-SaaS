# SSH Key Setup Guide for SBS29 (Training Server)

**Run on**: sbs29 (129.254.202.29)  
**Purpose**: Allow worker nodes to SSH in and transfer models  

---

## 🔑 Quick Method (Interactive Script)

Run this on sbs29:

```bash
bash /home/SBS29_ADD_WORKER_KEYS.sh
```

The script will:
1. Prompt you for each worker's SSH key
2. Add them to `~/.ssh/authorized_keys`
3. Set correct permissions

---

## 📋 Manual Method

### Step 1: On Worker Node (e.g., JW2)

Run the deployment script. It will show:

```
📋 YOUR SSH PUBLIC KEY (add this to sbs29's ~/.ssh/authorized_keys):
════════════════════════════════════════════════════════════════════
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAbCdEfG... jw2-cleaner
════════════════════════════════════════════════════════════════════
```

**Copy that entire line** (starting with `ssh-ed25519`)

### Step 2: On SBS29 (Training Server)

```bash
# Create/ensure authorized_keys exists
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Add the key (replace with actual key from worker)
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAbCdEfG... jw2-cleaner' >> ~/.ssh/authorized_keys
```

### Step 3: Repeat for Each Worker

Add keys for:
- ✅ jw2 (Cleaner)
- ✅ jw3 (Describer)  
- ✅ kcloud (Paraphraser)

---

## ✅ Verify Keys Are Added

```bash
cat ~/.ssh/authorized_keys
```

Should show 3 keys (one for each worker).

---

## 🔍 Test Connection (from worker)

After adding key on sbs29, test from worker:

```bash
# On jw2/jw3/kcloud:
ssh root@129.254.202.29 "echo OK"
```

Should print `OK` without password prompt.

---

## 🐛 Troubleshooting

### "Permission denied (publickey)"

**Check on sbs29:**
```bash
# Correct permissions?
ls -la ~/.ssh/
# Should be: drwx------ (700) for .ssh/
# Should be: -rw------- (600) for authorized_keys

# Key exists?
grep "jw2-cleaner\|jw3-describer\|kcloud-paraphraser" ~/.ssh/authorized_keys
```

**Fix permissions:**
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### "Connection refused"

Check if SSH service is running on sbs29:
```bash
sudo systemctl status sshd
```

### Firewall blocking?

```bash
# Check if port 22 is open
sudo firewall-cmd --list-all
```

---

## 📝 Expected authorized_keys Content

After adding all 3 worker keys:

```
ssh-ed25519 AAAAC3Nza... jw2-cleaner
ssh-ed25519 AAAAC3Nza... jw3-describer
ssh-ed25519 AAAAC3Nza... kcloud-paraphraser
```

---

## 🔄 Workflow Summary

1. **On worker**: Run `COPY_PASTE_<node>.sh`
2. **Script pauses**: Shows SSH public key
3. **On sbs29**: Add key to `~/.ssh/authorized_keys`
4. **On worker**: Press Enter to continue
5. **Script**: Tests connection and proceeds with model transfer

---

**Tip**: Use the automated script (`SBS29_ADD_WORKER_KEYS.sh`) for easier setup!

