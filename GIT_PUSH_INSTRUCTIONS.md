# Git Push Instructions

## Manual Steps to Push to GitHub

### 1. Install Git
Download and install Git from: https://git-scm.com/download/win

Or using winget:
```powershell
winget install --id Git.Git -e
```

### 2. Close and Reopen PowerShell/Terminal
This is required for Git to be recognized in PATH

### 3. Configure Git (First time only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 4. Initialize and Push Repository

```bash
# Navigate to project directory
cd C:\honeypot-project

# Initialize git repository
git init

# Add remote repository
git remote add origin https://github.com/ayaanmalhotra7777/honeypotscam.git

# Add all files (respecting .gitignore)
git add .

# Commit changes
git commit -m "Initial commit: Honeypot scam detection API with 96% accuracy"

# Push to GitHub
git push -u origin main
```

If the push fails with "main" branch, try:
```bash
git branch -M main
git push -u origin main
```

Or use "master" instead:
```bash
git push -u origin master
```

### 5. Authentication

GitHub may prompt for authentication. Use one of these methods:

**Option A: Personal Access Token (Recommended)**
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select `repo` scope
4. Use token as password when prompted

**Option B: GitHub CLI**
```bash
winget install GitHub.cli
gh auth login
```

**Option C: GitHub Desktop**
1. Download from https://desktop.github.com/
2. Sign in
3. Add repository from "Add Local Repository"
4. Push to GitHub

## Quick Command Summary

After Git is installed and terminal is reopened:

```powershell
cd C:\honeypot-project
git init
git remote add origin https://github.com/ayaanmalhotra7777/honeypotscam.git
git add .
git commit -m "Initial commit: Honeypot API with 96% accuracy"
git branch -M main
git push -u origin main
```

## Files That Will Be Pushed

✅ **Included**:
- All Python source files (*.py)
- requirements.txt
- README.md
- .gitignore
- static/chat.html

❌ **Excluded** (via .gitignore):
- api.env (contains API key)
- data/ (SQLite database)
- logs/ (CSV logs)
- scam_conversations/ (saved conversations)
- __pycache__/
- *.db, *.log files

## Verify Repository

After pushing, visit:
https://github.com/ayaanmalhotra7777/honeypotscam

You should see all your files except those in .gitignore
