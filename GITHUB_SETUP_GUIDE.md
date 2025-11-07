# GitHub with Cursor - Setup Guide

## Git Status
✅ **Git is already installed** (version 2.33.0.windows.1)

## Quick Start

### 1. Initialize Git Repository (if not already done)
```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. Connect to GitHub

#### Option A: Create a new repository on GitHub first
1. Go to [github.com](https://github.com) and sign in
2. Click the "+" icon → "New repository"
3. Name your repository (e.g., "project-signals")
4. **Don't** initialize with README, .gitignore, or license (we'll do that locally)
5. Copy the repository URL (HTTPS or SSH)

#### Option B: Use existing repository
1. Get the repository URL from GitHub

### 3. Add GitHub Remote
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
# OR if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
```

### 4. Push to GitHub
```bash
git branch -M main
git push -u origin main
```

## Using GitHub in Cursor

### Built-in Git Features

Cursor has excellent Git integration built-in:

1. **Source Control Panel** (Ctrl+Shift+G)
   - View all changed files
   - Stage/unstage changes
   - Commit changes
   - Push/pull from remote

2. **Git Status Bar** (bottom of Cursor)
   - Shows current branch
   - Shows pending changes
   - Quick access to Git commands

3. **Inline Git Features**
   - Red/green indicators show line changes
   - Hover to see commit history
   - Right-click files for Git options

### Common Git Commands in Cursor Terminal

#### Daily Workflow
```bash
# Check status
git status

# Stage changes
git add .
# OR stage specific file
git add path/to/file.py

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull latest changes
git pull

# Create and switch to new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Merge branch
git checkout main
git merge feature/new-feature
```

### Configure Git (if not already done)

```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Set default editor (optional)
git config --global core.editor "code --wait"
```

## Best Practices

### 1. Create a .gitignore file
Add this to ignore unnecessary files:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
data/
*.log
.env
.env.local
```

### 2. Commit Often
- Make small, focused commits
- Write clear commit messages
- Commit related changes together

### 3. Use Branches
- `main` or `master`: Production-ready code
- `develop`: Development branch
- `feature/name`: New features
- `bugfix/name`: Bug fixes

### 4. Pull Before Push
Always pull latest changes before pushing:
```bash
git pull origin main
git push origin main
```

## GitHub Authentication

### Using HTTPS
1. GitHub will prompt for credentials
2. For better security, use a Personal Access Token instead of password:
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `repo` scope
   - Use token as password when prompted

### Using SSH (Recommended)
1. Generate SSH key (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```
2. Add SSH key to ssh-agent:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```
3. Copy public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
4. Add to GitHub: Settings → SSH and GPG keys → New SSH key
5. Test connection:
   ```bash
   ssh -T git@github.com
   ```

## Cursor-Specific Tips

1. **Git Integration**: Cursor automatically detects Git repositories
2. **Commit Panel**: Use Ctrl+Shift+G to open source control
3. **Diff View**: Click any file in source control to see changes
4. **Branch Switching**: Click branch name in status bar to switch
5. **GitLens Extension**: Consider installing GitLens for enhanced Git features (if not already installed)

## Troubleshooting

### Authentication Issues
- Use Personal Access Token for HTTPS
- Or set up SSH keys

### Merge Conflicts
1. Open conflicting files in Cursor
2. Look for conflict markers: `<<<<<<<`, `=======`, `>>>>>>>`
3. Resolve conflicts manually
4. Stage resolved files: `git add .`
5. Complete merge: `git commit`

### Undo Last Commit (before pushing)
```bash
git reset --soft HEAD~1
```

### View Remote URL
```bash
git remote -v
```

## Next Steps

1. ✅ Git is installed
2. ⏭️ Initialize repository: `git init`
3. ⏭️ Create .gitignore file
4. ⏭️ Make initial commit
5. ⏭️ Create GitHub repository
6. ⏭️ Connect remote and push

---

**Need Help?**
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

