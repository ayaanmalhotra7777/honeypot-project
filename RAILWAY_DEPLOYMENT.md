# Railway Deployment Guide

## ✅ What's Already Set Up

Your honeypot is ready for Railway deployment with:
- ✓ `Dockerfile` - Docker container configuration
- ✓ `requirements.txt` - All dependencies listed
- ✓ `railway.json` - Railway builder config
- ✓ `.dockerignore` - Optimized Docker image

## 🚀 Deploy to Railway in 5 Minutes

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Connect your GitHub account

### Step 2: Create New Project
1. Click "Create New Project"
2. Select "Deploy from GitHub Repo"
3. Search for `honeypotscam` repository
4. Click "Deploy Now"

### Step 3: Set Environment Variables
1. In Railway Dashboard, go to "Variables"
2. Add your Gemini API key:
   ```
   API_KEY=your_gemini_api_key_here
   ```
3. Save and trigger redeploy

### Step 4: View Logs
1. Click "Logs" tab to see deployment progress
2. Wait for "Application running on http://0.0.0.0:8000"
3. Copy the public URL from the project

### Step 5: Access Your Honeypot
Railway provides a public URL like: `https://honeypot-production-xxxx.railway.app`

Access:
- **Web Chat**: `https://your-railway-url/chat`
- **API Endpoint**: `https://your-railway-url/api/honeypot`
- **Health Check**: `https://your-railway-url/health`

## 🔧 Manual GitHub Integration

If you deployed with a fork/different repo:

```bash
# In Railway Dashboard → Project Settings → GitHub:
1. Repository: ayaanmalhotra7777/honeypotscam
2. Branch: main
3. Auto-deploy: Enable
```

## 📊 Environment Variables on Railway

| Variable | Value |
|----------|-------|
| `API_KEY` | Your Gemini API key |
| `PORT` | 8000 (auto-set) |

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Railway should auto-install from `requirements.txt`. If not:
1. Check project logs for build errors
2. Redeploy: Project Settings → Redeploy
3. Verify `requirements.txt` is in root directory

### Error: "API key expired"
**Solution**: Update `API_KEY` variable in Railway Dashboard:
1. Variables tab
2. Change API_KEY value
3. Save and redeploy

### Slow Deployment
- First deploy takes 2-3 minutes (image build)
- Subsequent deploys are faster
- Check "Logs" tab for progress

### Application Not Starting
1. Click "Logs" tab
2. Look for error messages
3. Common fixes:
   - Ensure `main.py` exists
   - Check API_KEY is set
   - Verify requirements.txt syntax

## 🔗 Public URL Use

Your Railway URL works with:
- External API testers
- Other applications
- ChatGPT plugins
- Mobile apps

Example API request:
```bash
curl -X POST https://your-railway-url/api/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: Ayaanmalhotra@1" \
  -d '{
    "sessionId": "test-1",
    "message": {
      "sender": "scammer",
      "text": "Your UPI will be blocked in 24 hours",
      "timestamp": "2026-02-05T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English"
    }
  }'
```

## 🚨 Important Notes

### Database Persistence
- SQLite database (`data/honeypot.db`) is **NOT persistent** on Railway
- Each redeploy creates a fresh database
- For persistence, upgrade Railway to use PostgreSQL:
  1. Create PostgreSQL plugin
  2. Update database connection in code
  3. Redeploy

### Scam Conversations
- Saved in `scam_conversations/` folder (ephemeral)
- Delete on each redeploy
- Solution: Store in external database or S3

### Logs Directory
- `logs/honeypot_events.csv` is **NOT persisted**
- For persistent logs, use:
  - PostgreSQL plugin
  - External logging service (Datadog, LogRocket, etc.)

### File Uploads/Exports
- Files created in `/app` will be lost on redeploy
- Use cloud storage (S3, Supabase) for persistence

## ✨ Production Best Practices

### 1. Use PostgreSQL for Data
```bash
# In Railway:
1. Add PostgreSQL plugin
2. Copy connection string
3. Update database code
4. Redeploy
```

### 2. Add Monitoring
```bash
# In Railway Settings:
1. Enable Health Check
2. Set endpoint: /health
3. Set interval: 30s
```

### 3. Set Up Alerts
```bash
# In Railway Alerts:
1. Add alert for deployment failure
2. Add alert for crash detection
3. Notify via email/webhook
```

### 4. Custom Domain (Optional)
```bash
# In Project Settings → Networking:
1. Add custom domain
2. Point DNS to Railway
3. Enable HTTPS (automatic)
```

## 📈 Scaling

Railway auto-scales, but to optimize:

```bash
# In Project Settings → Scaling:
- Min instances: 1
- Max instances: 3
- Trigger: CPU >70% or Memory >80%
```

## 💰 Cost

Railway pricing (as of Feb 2026):
- **Free tier**: $5 credits/month
- **Hobby plan**: $5 + usage
- **Pro plan**: $20/month + usage

Honeypot runs well on free tier.

## 🎉 Deployment Complete!

Your honeypot is now:
- ✅ Publicly accessible
- ✅ Auto-scaling
- ✅ HTTPS enabled
- ✅ Health monitored
- ✅ Ready for production

Next steps:
1. Share your public URL
2. Test with external API clients
3. Monitor logs for scam detections
4. Scale as needed

---

**Questions?** Check Railway docs: https://docs.railway.app
