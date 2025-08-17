# TWITTER API SETUP GUIDE

## Step 1: Get Twitter Developer Account
1. Go to: https://developer.twitter.com/
2. Apply for Twitter Developer Account
3. Create a new Twitter App

## Step 2: Get API Keys
After approval, you'll get:
- API Key (Consumer Key)
- API Secret Key (Consumer Secret) 
- Access Token
- Access Token Secret

## Step 3: Update config.yaml
Replace these placeholders with your real keys:

```yaml
social_media:
  twitter:
    enabled: true
    api_key: "YOUR_ACTUAL_API_KEY"
    api_secret: "YOUR_ACTUAL_API_SECRET" 
    access_token: "YOUR_ACTUAL_ACCESS_TOKEN"
    access_token_secret: "YOUR_ACTUAL_ACCESS_TOKEN_SECRET"
    auto_post: true
```

## Step 4: Install Required Package
```bash
pip install tweepy>=4.14.0
```

## Step 5: Test Real Publishing
Once configured, the system will actually post to Twitter!
