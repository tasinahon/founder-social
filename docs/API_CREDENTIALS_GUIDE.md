# 🔑 Complete Guide: How to Get API Credentials for Social Media Publishing

## 🐦 TWITTER/X API CREDENTIALS

### What You Need:
- **API Key** (Consumer Key)
- **API Secret Key** (Consumer Secret)  
- **Access Token**
- **Access Token Secret**

### Step-by-Step Process:

#### 1. Apply for Twitter Developer Account
- Go to: **https://developer.twitter.com/**
- Click "Apply for a developer account"
- Choose "Making a bot" or "Academic researcher" 
- Fill out the application form:
  - **Use case**: "Building a content publishing tool for startup marketing"
  - **Will you make Twitter content available?**: No
  - **Will you use Twitter data for analysis?**: No
  - **Will you display Tweets outside Twitter?**: No

#### 2. Wait for Approval
- Usually takes **24-48 hours**
- You'll get an email when approved

#### 3. Create Your App
- Go to Developer Portal: **https://developer.twitter.com/en/portal/dashboard**
- Click "Create App"
- Fill in app details:
  - **App name**: "SocioFi Content Publisher" 
  - **Description**: "AI-powered content publishing for startup marketing"
  - **Website**: "https://sociofitechnology.com"

#### 4. Get Your Keys
- Go to your app → "Keys and tokens" tab
- **API Key & Secret**: Click "Regenerate" if needed
- **Access Token & Secret**: Click "Generate" 

#### 5. Update config.yaml:
```yaml
social_media:
  twitter:
    enabled: true
    api_key: "YOUR_ACTUAL_API_KEY_HERE"
    api_secret: "YOUR_ACTUAL_API_SECRET_HERE"
    access_token: "YOUR_ACTUAL_ACCESS_TOKEN_HERE"
    access_token_secret: "YOUR_ACTUAL_ACCESS_TOKEN_SECRET_HERE"
    auto_post: true
```

---

## 💼 LINKEDIN API CREDENTIALS

### What You Need:
- **Client ID**
- **Client Secret**
- **Access Token** (OAuth 2.0)

### Step-by-Step Process:

#### 1. Create LinkedIn App
- Go to: **https://developer.linkedin.com/**
- Click "Create app"
- Fill in details:
  - **App name**: "SocioFi Content Publisher"
  - **LinkedIn Page**: Your company page (create one if needed)
  - **Privacy policy URL**: "https://sociofitechnology.com/privacy"
  - **App logo**: Upload your company logo

#### 2. Configure App Permissions
- Go to "Products" tab
- Request access to:
  - **Share on LinkedIn** (for posting)
  - **Marketing Developer Platform** (for company pages)

#### 3. Get Client Credentials
- Go to "Auth" tab
- Copy **Client ID** and **Client Secret**

#### 4. Generate Access Token
- Use LinkedIn OAuth 2.0 flow OR
- Use tools like Postman to get token
- Scope needed: `w_member_social,w_organization_social`

#### 5. Update config.yaml:
```yaml
social_media:
  linkedin:
    enabled: true
    client_id: "YOUR_LINKEDIN_CLIENT_ID"
    client_secret: "YOUR_LINKEDIN_CLIENT_SECRET"
    access_token: "YOUR_LINKEDIN_ACCESS_TOKEN"
    auto_post: true
```

---

## 📘 FACEBOOK API CREDENTIALS

### What You Need:
- **App ID**
- **App Secret**
- **Page Access Token**
- **Page ID**

### Step-by-Step Process:

#### 1. Create Facebook App
- Go to: **https://developers.facebook.com/**
- Click **"My Apps"** (top right corner)
- Click **"Create App"**
- Choose **"Business"** type
- Fill in app details:
  - **App name**: "SocioFi Content Publisher"
  - **Contact email**: your email
- Click **"Create App"**

#### 2. Add Required Products/APIs
In your App Dashboard, find **"Add Products to Your App"** section:
- **Facebook Login** → Click **"Set Up"** 
- **Pages API** → Click **"Set Up"**
- **Instagram Basic Display** → Click **"Set Up"** (optional, for Instagram)

#### 3. Get App Credentials
- Go to **Settings** → **Basic** (left sidebar)
- Copy your **App ID** 
- Copy your **App Secret** (click "Show" button)

#### 4. Create/Setup Facebook Page
- Create a Facebook Page: https://www.facebook.com/pages/create
- Choose **"Business or Brand"**
- Fill in your business details
- Once created, go to **About** tab → scroll down to find **Page ID**

#### 5. Get Page Access Token
- Go to **Tools** → **Graph API Explorer** in your app dashboard
- Select your app from dropdown (top left)
- Select your page from dropdown
- Click **"Generate Access Token"**
- Grant **"pages_manage_posts"** permission
- Copy the generated token

#### 6. Update config.yaml:
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

---

## 📝 WORDPRESS CREDENTIALS

### What You Need:
- **WordPress Site URL**
- **Username**
- **Password** (or Application Password)

### Step-by-Step Process:

#### Option 1: WordPress.com
1. Create account at **https://wordpress.com/**
2. Create a new site
3. Go to Settings → Security
4. Generate "Application Password"
5. Use this instead of regular password

#### Option 2: Self-Hosted WordPress
1. Install WordPress on your hosting
2. Enable XML-RPC (usually enabled by default)
3. Create admin user account
4. Use admin credentials

#### 3. Update config.yaml:
```yaml
blog_platforms:
  wordpress:
    enabled: true
    url: "https://yourblog.wordpress.com"
    username: "your_username"
    password: "your_application_password"
    auto_post: true
```

---

## 🚀 QUICK START RECOMMENDATION

### Start with Twitter (Easiest):
1. **Twitter approval is fastest** (24-48 hours)
2. **Most straightforward setup**
3. **Best for testing the system**

### Implementation Order:
1. ✅ **Twitter** (Start here)
2. ✅ **WordPress** (Easy to set up)
3. ✅ **LinkedIn** (More complex OAuth)
4. ✅ **Facebook** (Most complex)

---

## 🔒 SECURITY BEST PRACTICES

### Keep Credentials Safe:
- ❌ Never commit API keys to Git
- ✅ Use environment variables in production
- ✅ Regenerate keys if compromised
- ✅ Use application-specific passwords

### Testing:
- ✅ Start with one platform
- ✅ Test with dummy content first
- ✅ Monitor API usage limits
- ✅ Check posts manually after automation

---

## 📞 NEED HELP?

### If Applications Get Rejected:
- **Twitter**: Be specific about use case, mention it's for legitimate business marketing
- **LinkedIn**: Ensure you have a complete LinkedIn company page
- **Facebook**: Provide detailed app description and privacy policy

### Common Issues:
- **Rate limits**: Most APIs have posting limits (Twitter: 300 tweets/3hrs)
- **Permissions**: Make sure you request correct scopes
- **Tokens expire**: LinkedIn tokens expire, need refresh mechanism

### Support Links:
- Twitter: https://developer.twitter.com/en/support
- LinkedIn: https://developer.linkedin.com/support  
- Facebook: https://developers.facebook.com/support/
