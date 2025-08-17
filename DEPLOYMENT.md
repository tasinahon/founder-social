# Deployment Guide for Founder Socials AI Agent

This guide covers multiple deployment options for your Founder Socials AI Agent.

## 🚀 Quick Deployment Options

### 1. Railway (Recommended - Easiest)

Railway is perfect for Python apps with built-in database support.

**Steps:**
1. Push your code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Click "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect the Dockerfile and deploy

**Environment Variables to Set in Railway:**
```
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
PORT=8000
ENVIRONMENT=production
```

**Cost:** $5/month (includes database)

### 2. Render

Great for Python apps with free tier available.

**Steps:**
1. Push code to GitHub
2. Go to [Render.com](https://render.com)
3. Create new "Web Service"
4. Connect your GitHub repo
5. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

**Cost:** Free tier available, paid plans from $7/month

### 3. Vercel (Serverless)

Good for lighter workloads with automatic scaling.

**Steps:**
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in your project directory
3. Follow the prompts

**Limitations:** Serverless functions have execution time limits (10 seconds on free tier)

### 4. Google Cloud Run

Enterprise-grade with pay-per-use pricing.

**Steps:**
1. Install Google Cloud CLI
2. Build and push Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/founder-socials
   gcloud run deploy --image gcr.io/PROJECT_ID/founder-socials --platform managed
   ```

## 🔧 Before Deploying

### 1. Set Up Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

**Required Environment Variables:**
- `OPENAI_API_KEY` or `AZURE_OPENAI_API_KEY`
- `TWITTER_CLIENT_ID` and `TWITTER_CLIENT_SECRET` (if using Twitter)
- `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` (if using LinkedIn)
- `FACEBOOK_APP_ID` and `FACEBOOK_APP_SECRET` (if using Facebook)

### 2. Update Redirect URIs

For social media OAuth, update your app settings:

**Twitter:** [developer.twitter.com](https://developer.twitter.com)
- Add redirect URI: `https://your-domain.com/auth/twitter/callback`

**LinkedIn:** [linkedin.com/developers](https://linkedin.com/developers)
- Add redirect URI: `https://your-domain.com/auth/linkedin/callback`

**Facebook:** [developers.facebook.com](https://developers.facebook.com)
- Add redirect URI: `https://your-domain.com/auth/facebook/callback`

### 3. Database Configuration

For production, consider using a managed database:

**Railway:** Includes PostgreSQL database
**Render:** Offers PostgreSQL add-on
**Vercel:** Use PlanetScale or Supabase

Update your `config/config.yaml`:
```yaml
database:
  url: ${DATABASE_URL}  # Set via environment variable
```

## 🐳 Docker Deployment

For custom deployments, use the included Dockerfile:

```bash
# Build image
docker build -t founder-socials .

# Run container
docker run -p 8000:8000 --env-file .env founder-socials
```

## 📊 Monitoring and Logs

### Health Check Endpoint
Your app includes a health check at `/api/health`

### Logging
Logs are configured for production. Check your platform's log viewer:
- **Railway:** Built-in log viewer
- **Render:** Logs tab in dashboard
- **Vercel:** Functions tab for serverless logs

## 🔒 Security Considerations

1. **Environment Variables:** Never commit API keys to git
2. **HTTPS:** All platforms provide SSL certificates automatically
3. **Rate Limiting:** Consider adding rate limiting for production
4. **Database Security:** Use managed databases with backup

## 🚀 Scaling

### Vertical Scaling
Increase memory/CPU allocation in your platform dashboard

### Horizontal Scaling
Most platforms support auto-scaling:
- **Railway:** Auto-scales based on load
- **Render:** Manual scaling in dashboard
- **Google Cloud Run:** Automatic scaling

## 📈 Cost Estimates

| Platform | Free Tier | Paid Starting | Database | SSL |
|----------|-----------|---------------|-----------|-----|
| Railway | 500 hours | $5/month | Included | ✅ |
| Render | 750 hours | $7/month | $7/month | ✅ |
| Vercel | 100GB-hrs | $20/month | External | ✅ |
| Google Cloud | $300 credit | Pay-per-use | Separate | ✅ |

## 🆘 Troubleshooting

### Common Issues:

1. **Import Errors:** Make sure all dependencies are in `requirements.txt`
2. **Port Issues:** Use `PORT` environment variable
3. **API Key Errors:** Check environment variable names
4. **Database Errors:** Ensure DATABASE_URL is set correctly

### Getting Help:
- Check platform documentation
- Review application logs
- Test locally with `python run.py`

## 🎯 Recommended Deployment

For most users, we recommend **Railway** because:
- ✅ Easy deployment from GitHub
- ✅ Includes database
- ✅ Automatic SSL
- ✅ Great developer experience
- ✅ Reasonable pricing

Deploy now: [railway.app](https://railway.app)
