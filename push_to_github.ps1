# PowerShell script to push honeypot to GitHub
# Run this AFTER installing Git and reopening terminal

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Honeypot GitHub Push Script" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git not found!" -ForegroundColor Red
    Write-Host "`nPlease install Git first:" -ForegroundColor Yellow
    Write-Host "  winget install --id Git.Git -e" -ForegroundColor White
    Write-Host "`nThen close and reopen PowerShell`n" -ForegroundColor Yellow
    exit 1
}

# Navigate to project directory
$projectPath = "C:\honeypot-project"
Set-Location $projectPath
Write-Host "✓ In directory: $projectPath" -ForegroundColor Green

# Initialize git repository
Write-Host "`nInitializing Git repository..." -ForegroundColor Yellow
git init

# Add remote
Write-Host "Adding remote repository..." -ForegroundColor Yellow
git remote add origin https://github.com/ayaanmalhotra7777/honeypotscam.git 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Remote already exists, updating..." -ForegroundColor Gray
    git remote set-url origin https://github.com/ayaanmalhotra7777/honeypotscam.git
}

# Stage all files
Write-Host "Staging files (respecting .gitignore)..." -ForegroundColor Yellow
git add .

# Show what will be committed
Write-Host "`nFiles to be committed:" -ForegroundColor Cyan
git status --short

# Commit
Write-Host "`nCommitting changes..." -ForegroundColor Yellow
git commit -m "Initial commit: Honeypot scam detection API with 96% accuracy

Features:
- 96% accuracy on 50-test suite
- Gemini Pro AI integration (free tier)
- Auto-stop on scam detection
- Web chat interface
- SQLite + CSV persistence
- Automatic TXT file export"

# Switch to main branch
Write-Host "Switching to main branch..." -ForegroundColor Yellow
git branch -M main

# Push to GitHub
Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
Write-Host "You may be prompted for authentication." -ForegroundColor Gray
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n============================================" -ForegroundColor Green
    Write-Host "  ✓ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "`nView your repository at:" -ForegroundColor Cyan
    Write-Host "  https://github.com/ayaanmalhotra7777/honeypotscam`n" -ForegroundColor White
} else {
    Write-Host "`n============================================" -ForegroundColor Red
    Write-Host "  ✗ Push failed!" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "`nPossible reasons:" -ForegroundColor Yellow
    Write-Host "  1. Authentication required (use Personal Access Token)" -ForegroundColor White
    Write-Host "  2. Repository doesn't exist on GitHub" -ForegroundColor White
    Write-Host "  3. No permission to push to this repository" -ForegroundColor White
    Write-Host "`nSee GIT_PUSH_INSTRUCTIONS.md for detailed help`n" -ForegroundColor Cyan
}
