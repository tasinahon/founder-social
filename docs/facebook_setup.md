# FACEBOOK API SETUP GUIDE

## 🤔 What is developers.facebook.com?
**developers.facebook.com** = Facebook's portal where you get **API keys** (permission slips) that let your Python code post to Facebook automatically.

## 🔄 How Publishing Works:
1. **Your web app** (localhost:8000) → **Your Python code** → **Facebook's servers** → **Your Facebook page**
2. The "API keys" are what allow your Python code to talk to Facebook's servers
3. Right now = MOCK posting (fake), With API keys = REAL posting

## Step 1: Get Facebook Developer Account  
1. Go to: https://developers.facebook.com/
2. **IMPORTANT**: Look for "Get Started" button (top right) OR "Build with us" menu
3. Click **"App Development"** or go directly to: **https://developers.facebook.com/apps/**
4. You should see a page titled **"My Apps"** with a blue **"Create App"** button
5. Click **"Create App"** button

## Step 2: Get Required Tokens (These are your "permission slips")
You need:
- **App ID** = Your app's unique identifier
- **App Secret** = Your app's password  
- **Page Access Token** = Permission to post to your specific page
- **Page ID** = Which page to post to

## Step 3: Update config.yaml
```yaml
social_media:
  facebook:
    enabled: true
    app_id: "YOUR_FACEBOOK_APP_ID"
    app_secret: "YOUR_FACEBOOK_APP_SECRET"
    access_token: "YOUR_PAGE_ACCESS_TOKEN" 
    page_id: "YOUR_FACEBOOK_PAGE_ID"
    auto_post: true
```

## Step 4: Install Package
```bash
pip install facebook-sdk>=3.1.0
```

## Step 5: Test Real Publishing
System will post to your Facebook Page!
