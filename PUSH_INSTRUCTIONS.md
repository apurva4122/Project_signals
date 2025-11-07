# Push Your Code to GitHub - Quick Instructions

## Method: Personal Access Token (Easiest)

### Step 1: Create a Personal Access Token
1. Go to: **https://github.com/settings/tokens/new**
2. Token name: `Project Signals`
3. Expiration: Choose (90 days, 1 year, or no expiration)
4. **Select scope**: Check ✅ **`repo`** (this is important!)
5. Click **"Generate token"** at the bottom
6. **COPY THE TOKEN** - it looks like `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - ⚠️ You won't be able to see it again after you leave this page!

### Step 2: Push Your Code
Run this command:
```bash
git push -u origin main
```

When prompted:
- **Username**: `apurva4122`
- **Password**: Paste your Personal Access Token (NOT your GitHub password)

---

## Alternative: Use Git Credential Manager (Windows)

If you have Git Credential Manager installed, it will prompt you in a popup window where you can:
- Enter username: `apurva4122`
- Enter password: Your Personal Access Token

---

**Quick Link to Create Token**: https://github.com/settings/tokens/new

