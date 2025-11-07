# Add SSH Key to GitHub - Quick Steps

## Your SSH Public Key:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKQ6abSFcb7elVs9E/jFVKcim/U+/kAK/rfr3MhtdSQH 84181959+apura4122@users.noreply.github.com
```

## Steps:

1. **Copy the key above** (the entire line starting with `ssh-ed25519`)

2. **Go to GitHub**:
   - Visit: https://github.com/settings/keys
   - Or: GitHub → Settings → SSH and GPG keys

3. **Add the key**:
   - Click **"New SSH key"**
   - Title: `Project Signals - Windows`
   - Key type: `Authentication Key`
   - Key: Paste the key above
   - Click **"Add SSH key"**

4. **Come back here** and I'll help you push the code!

---

**Alternative Quick Method**: Use Personal Access Token (no SSH setup needed)
- Go to: https://github.com/settings/tokens/new
- Create token with `repo` scope
- Use it as password when pushing

