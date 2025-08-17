# 🚀 COMPLETE DEPLOYMENT COMMANDS WITH ALL SECRETS

## 📋 **COMPLETE ENVIRONMENT VARIABLES LIST**

Since your `config.yaml` contains ALL these sensitive credentials, here's the complete environment variables setup for deployment:

### **For Railway Deployment:**

1. **Go to https://railway.app**
2. **Create New Project → Deploy from GitHub repo → Connect GitHub**
3. **Set ALL these environment variables in Railway dashboard:**

```bash
# ============================================
# AI PROVIDER CREDENTIALS
# ============================================
AZURE_OPENAI_API_KEY=A02OOjVTyTDPX0UFljXCRWNEazqTF5Sdq5hlXV3CN2eVD1ljSHWwJQQJ99ALAC5RqLJXJ3w3AAAAACOGfOHQ
AZURE_OPENAI_ENDPOINT=https://ai-founder-3699.openai.azure.com/
GPT4O_API_KEY=A02OOjVTyTDPX0UFljXCRWNEazqTF5Sdq5hlXV3CN2eVD1ljSHWwJQQJ99ALAC5RqLJXJ3w3AAAAACOGfOHQ
GPT4O_ENDPOINT=https://ai-founder-3699.openai.azure.com/openai/deployments/gpt-4o
DEEPSEEK_R1_API_KEY=A02OOjVTyTDPX0UFljXCRWNEazqTF5Sdq5hlXV3CN2eVD1ljSHWwJQQJ99ALAC5RqLJXJ3w3AAAAACOGfOHQ
DEEPSEEK_R1_ENDPOINT=https://ai-founder-3699.openai.azure.com/

# ============================================
# TWITTER/X CREDENTIALS
# ============================================
TWITTER_CLIENT_ID=T05ETUk4WlBaZ2ZaekhkaDg0TUo6MTpjaQ
TWITTER_CLIENT_SECRET=Zo4nqnAAc_Cv9DGZf1DklDQzkGoR1uQPiR2y0b50CevzKzQWFV
TWITTER_API_KEY=zSR62skZ3qEQa7M6V4qbazQu4
TWITTER_API_SECRET=70zv3ykcziqL6l91gZEIodRl7f6uRJ2ipE2GKWAxpFlESKKj5A
TWITTER_ACCESS_TOKEN=1911985732769710080-yzoMT2e9n66ELzhDt5kcIiO17jO7AK
TWITTER_ACCESS_TOKEN_SECRET=Ss5zANskebyh7TwKCh2EgKd4hAlcm2y4YjSKR01DoStPT
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAANzY3QEAAAAAaqdyQoha4I%2BfdGd5LtD2vV7YNqo%3DHO1m5gfXf2PXMPeKANXkusRl4qIgedMRes9Lh77Aw58fYVuE18

# ============================================
# FACEBOOK CREDENTIALS
# ============================================
FACEBOOK_APP_ID=1937644817012952
FACEBOOK_APP_SECRET=6753b4e4cb87066014d9ec1cd7bb34f3
FACEBOOK_ACCESS_TOKEN=EAAbiRxcE2NgBPJlxEhD5Ncqt4wvJkyZCXJcXGtKGjIVZBCgKyIZBOWnJaws1FFuZBhmgGfUXO2ABlQZBvK2QzXg7FkIHM6BVqWJb2L9KpDKZAhxOEQlEYUySY1wrp7JZBhlorsG5QxqxHY07ELeO8PAYE6RlPkXgwX1GhvRVH4BwZAF0JklqutKydX3ZAw9OISDYL5tezQo3X
FACEBOOK_PAGE_ID=564794600044137

# ============================================
# LINKEDIN CREDENTIALS
# ============================================
LINKEDIN_CLIENT_ID=78ye1cdk35bvui
LINKEDIN_CLIENT_SECRET=WPL_AP1.La452ZR7LbixU1Th.91JzRQ==
LINKEDIN_ACCESS_TOKEN=AQVNhk5hwyo-loIMdBo2aHt6s_w73m-LbO9pg-u1f5460zOCEdNqExdmfU_3USBNmIT8blmELErQRQqMghgs967u6vbQ--0sZENahSXpQStsUDvDVFa7X0L-Mo2i9ifDXBXOx4lFORxR-2bcF_iWEuoCD8ihLF88FQ3G8FzSzk2waaK0p0pngtyYp0gD3kwhWr9bwe_duWcpp6_GUni1UvaBWrgIGeaFPglmqMOBXHjxvqVrm0zBG8sssbc9svT8QvNug5A3SfQ6hl5yTGk7YHVA_paNveBkqaNvp7Eq9TEWC05F4ioKWGToAeeLmMwDMWDQbItmZVwjzYOewk6q9qfiGFASaw
LINKEDIN_COMPANY_ID=108288876

# ============================================
# APPLICATION SETTINGS
# ============================================
ENVIRONMENT=production
DEBUG=false
PORT=8000
SECRET_KEY=super_secure_random_key_change_this_12345

# ============================================
# STARTUP INFO
# ============================================
STARTUP_NAME=Your Startup Name
STARTUP_INDUSTRY=Technology
STARTUP_WEBSITE=https://yourstartup.com
```

## 🚀 **DEPLOYMENT COMMANDS**

### **Option 1: Railway (Recommended)**

```powershell
# 1. Go to https://railway.app
# 2. Sign up/login with GitHub
# 3. Click "New Project"
# 4. Select "Deploy from GitHub repo"
# 5. Connect your GitHub account
# 6. Select tasinahon/founder-social repository
# 7. Railway will auto-detect the Dockerfile
# 8. Set ALL the environment variables above in Variables tab
# 9. Deploy!
```

**Railway URL after deployment:** `https://your-app-name.up.railway.app`

### **Option 2: Render**

```powershell
# 1. Go to https://render.com
# 2. Sign up/login with GitHub
# 3. Click "New" → "Web Service"
# 4. Connect GitHub and select tasinahon/founder-social
# 5. Configure:
```

**Render Settings:**
- **Name:** `founder-socials`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:** Add all the variables above

### **Option 3: Direct Docker Deployment**

```powershell
# Build and run locally with environment variables
docker build -t founder-socials .

# Create .env file with all variables above, then:
docker run -p 8000:8000 --env-file .env founder-socials
```

### **Option 4: Heroku**

```powershell
# Install Heroku CLI, then:
heroku create your-app-name
heroku config:set AZURE_OPENAI_API_KEY=A02OOjVTyTDPX0UFljXCRWNEazqTF5Sdq5hlXV3CN2eVD1ljSHWwJQQJ99ALAC5RqLJXJ3w3AAAAACOGfOHQ
heroku config:set GPT4O_API_KEY=A02OOjVTyTDPX0UFljXCRWNEazqTF5Sdq5hlXV3CN2eVD1ljSHWwJQQJ99ALAC5RqLJXJ3w3AAAAACOGfOHQ
# ... set all other environment variables
git push heroku main
```

## 🔧 **MODIFY APPLICATION TO USE ENVIRONMENT VARIABLES**

To make your app use environment variables instead of config.yaml:
