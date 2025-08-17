# 📋 API CREDENTIALS CHECKLIST

## ✅ WHAT YOU NEED TO COLLECT:

### 🐦 Twitter/X:
- [ ] API Key (Consumer Key)
- [ ] API Secret Key (Consumer Secret)
- [ ] Access Token  
- [ ] Access Token Secret
- **Get from**: https://developer.twitter.com/

### 💼 LinkedIn:
- [ ] Client ID
- [ ] Client Secret
- [ ] Access Token (OAuth 2.0)
- **Get from**: https://developer.linkedin.com/

### 📘 Facebook:
- [ ] App ID
- [ ] App Secret
- [ ] Page Access Token
- [ ] Page ID
- **Get from**: https://developers.facebook.com/

### 📝 WordPress:
- [ ] Site URL
- [ ] Username
- [ ] Password/Application Password
- **Get from**: Any WordPress site

---

## 🔧 CONFIGURATION TEMPLATE

Copy this template and replace with your actual credentials:

```yaml
# Social Media Platforms
social_media:
  twitter:
    enabled: true
    api_key: "REPLACE_WITH_YOUR_TWITTER_API_KEY"
    api_secret: "REPLACE_WITH_YOUR_TWITTER_API_SECRET"
    access_token: "REPLACE_WITH_YOUR_TWITTER_ACCESS_TOKEN"
    access_token_secret: "REPLACE_WITH_YOUR_TWITTER_ACCESS_TOKEN_SECRET"
    auto_post: true
  
  linkedin:
    enabled: true
    client_id: "REPLACE_WITH_YOUR_LINKEDIN_CLIENT_ID"
    client_secret: "REPLACE_WITH_YOUR_LINKEDIN_CLIENT_SECRET"
    access_token: "REPLACE_WITH_YOUR_LINKEDIN_ACCESS_TOKEN"
    auto_post: true
  
  facebook:
    enabled: true
    app_id: "REPLACE_WITH_YOUR_FACEBOOK_APP_ID"
    app_secret: "REPLACE_WITH_YOUR_FACEBOOK_APP_SECRET"
    access_token: "REPLACE_WITH_YOUR_FACEBOOK_ACCESS_TOKEN"
    page_id: "REPLACE_WITH_YOUR_FACEBOOK_PAGE_ID"
    auto_post: true

# Blog Platforms
blog_platforms:
  wordpress:
    enabled: true
    url: "REPLACE_WITH_YOUR_WORDPRESS_URL"
    username: "REPLACE_WITH_YOUR_WORDPRESS_USERNAME"
    password: "REPLACE_WITH_YOUR_WORDPRESS_PASSWORD"
    auto_post: true
```

---

## 🚀 TESTING STEPS:

### After Adding Credentials:

1. **Update config.yaml** with real credentials
2. **Restart server**: `python run.py`
3. **Run test**: `python test_publishing.py`
4. **Check your accounts** - posts should appear!

### Expected Results:
- ✅ Posts appear on your social media
- ✅ Server logs show real API responses  
- ✅ No "Mock publish" messages
- ✅ Actual engagement data

---

## ⏰ TIMELINE EXPECTATIONS:

- **Twitter**: 24-48 hours approval
- **WordPress**: Immediate (just need a blog)
- **LinkedIn**: 1-7 days approval
- **Facebook**: 1-14 days approval

## 💡 PRO TIP:
Start with **Twitter + WordPress** - they're the easiest to set up and will let you test the system immediately!
