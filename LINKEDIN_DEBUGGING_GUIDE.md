# LinkedIn Developer App Setup Guide

## Current Issue
Your LinkedIn access token is valid (confirmed by introspection) but ALL API endpoints return 401 "Invalid access token". This suggests an app-level issue, not a token issue.

## Immediate Action Required

### Check Your Current App Status
1. Go to: https://www.linkedin.com/developers/apps
2. Find your app: "785s08itvgnr6u"
3. Check the "Products" tab - ensure these are APPROVED:
   - ✅ Sign In with LinkedIn using OpenID Connect
   - ✅ Share on LinkedIn  
   - ✅ Marketing Developer Platform (for company posting)

### Look for These Warning Signs:
- ❌ App status: "In Review" or "Suspended"
- ❌ Products status: "Pending" or "Rejected"
- ❌ Verification required messages
- ❌ App access restrictions

## If App Has Issues: Create New App

### Step 1: Create New LinkedIn App
1. Go to: https://www.linkedin.com/developers/apps
2. Click "Create App"
3. Fill out:
   - App name: "Founder Socials AI v2"
   - LinkedIn Page: Select your company page
   - App logo: Upload any logo
   - Legal agreement: Check the box

### Step 2: Configure Products
Request these products in order:
1. "Sign In with LinkedIn using OpenID Connect" (Usually auto-approved)
2. "Share on LinkedIn" (Usually auto-approved)
3. "Marketing Developer Platform" (May require review)

### Step 3: Update Redirect URLs
Add: http://localhost:8000/auth/linkedin/callback

### Step 4: Get New Credentials
- Copy Client ID
- Copy Client Secret
- Update config.yaml

### Step 5: Generate Fresh Token
Use the OAuth flow to generate a token with the new app credentials.

## Alternative: Try with Different Scopes

Your current token has these scopes:
- email,openid,profile (basic)
- r_1st_connections_size (connections)
- r_ads,r_ads_reporting,rw_ads (advertising - might be the issue)
- r_basicprofile (deprecated?)
- r_organization_admin,r_organization_social,rw_organization_admin,w_organization_social (company)
- w_member_social (personal posting)

The issue might be with the advertising scopes or deprecated scopes.

## Next Steps
1. Check your app status in LinkedIn Developer Console
2. If app has issues, create a new app
3. If app looks fine, try contacting LinkedIn Developer Support

Let me know what you find in the Developer Console!
