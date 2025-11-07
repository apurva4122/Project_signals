# GitHub Authentication Setup

## Option 1: Personal Access Token (Recommended - Quickest)

### Step 1: Create a Personal Access Token on GitHub

1. Go to GitHub → Click your profile picture (top right) → **Settings**
2. Scroll down and click **Developer settings** (left sidebar)
3. Click **Personal access tokens** → **Tokens (classic)**
4. Click **Generate new token** → **Generate new token (classic)**
5. Give it a name: `Project Signals Local Dev`
6. Set expiration: Choose your preference (90 days, 1 year, or no expiration)
7. Select scopes: Check **`repo`** (this gives full control of private repositories)
8. Click **Generate token** at the bottom
9. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!
   - It will look like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Use the Token to Push

When you run `git push`, GitHub will prompt for:
- **Username**: `apurva4122`
- **Password**: Paste your Personal Access Token (NOT your GitHub password)

Or you can configure Git Credential Manager to store it:

```bash
# Windows Credential Manager will prompt you
git push -u origin main
```

When prompted:
- Username: `apurva4122`
- Password: `YOUR_PERSONAL_ACCESS_TOKEN`

---

## Option 2: SSH Keys (More Secure - Long-term)

### Step 1: Generate SSH Key

```bash
ssh-keygen -t ed25519 -C "84181959+apura4122@users.noreply.github.com"
```

- Press Enter to accept default location
- Press Enter twice for no passphrase (or enter one if you want extra security)

### Step 2: Add SSH Key to ssh-agent

```bash
# Start ssh-agent
Start-Service ssh-agent

# Add your key
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

### Step 3: Copy Your Public Key

```bash
cat $env:USERPROFILE\.ssh\id_ed25519.pub
```

Copy the entire output (starts with `ssh-ed25519`)

### Step 4: Add SSH Key to GitHub

1. Go to GitHub → Settings → **SSH and GPG keys**
2. Click **New SSH key**
3. Title: `Project Signals - Windows`
4. Key: Paste your public key
5. Click **Add SSH key**

### Step 5: Change Remote to SSH

```bash
git remote set-url origin git@github.com:apurva4122/Project_signals.git
```

### Step 6: Test Connection

```bash
ssh -T git@github.com
```

You should see: `Hi apurva4122! You've successfully authenticated...`

### Step 7: Push

```bash
git push -u origin main
```

---

## Quick Start (Personal Access Token)

If you want to push right now:

1. **Create token**: https://github.com/settings/tokens/new
   - Name: `Project Signals`
   - Check `repo` scope
   - Generate and copy token

2. **Push with token**:
   ```bash
   git push -u origin main
   ```
   - Username: `apurva4122`
   - Password: `YOUR_TOKEN_HERE`

---

**Need help?** Let me know which method you prefer!

