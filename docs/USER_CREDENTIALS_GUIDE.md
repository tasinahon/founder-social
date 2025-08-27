# User Configuration Template for Founder Socials AI Agent

This template shows what API credentials you need to configure for each platform.

## Facebook Configuration

To set up Facebook publishing, you'll need:

1. **App ID**: Your Facebook App ID
   - Get from: https://developers.facebook.com/
   - Create a new app if you don't have one

2. **App Secret**: Your Facebook App Secret  
   - Found in your app settings on Facebook Developers
   - Keep this secret and secure

3. **Page Access Token**: A token for your Facebook page
   - Generate in your app's tools section
   - Must have "pages_manage_posts" permission
   - Should be a long-lived token

4. **Page ID**: Your Facebook page ID
   - Found in your page settings or page info

## LinkedIn Configuration

To set up LinkedIn publishing, you'll need:

1. **Client ID**: Your LinkedIn app client ID
   - Get from: https://developer.linkedin.com/
   - Create a new app for your company

2. **Client Secret**: Your LinkedIn app client secret
   - Found in your app settings
   - Keep this secret and secure

3. **Access Token**: A user or company access token
   - Generate using LinkedIn OAuth flow
   - Must have "w_member_social" scope for personal posts
   - Must have "w_organization_social" scope for company posts

4. **Company ID** (Optional): For posting as a company
   - Your LinkedIn company/organization ID
   - Only needed if posting as a company page

## Twitter/X Configuration

To set up Twitter publishing, you'll need:

1. **API Key**: Your Twitter app API key
   - Get from: https://developer.twitter.com/
   - Create a new app in the developer portal

2. **API Secret**: Your Twitter app API secret
   - Found in your app keys and tokens
   - Keep this secret and secure

3. **Access Token**: Your user access token
   - Generate in your app settings
   - Must have read and write permissions

4. **Access Token Secret**: Secret for your access token
   - Generated with your access token
   - Keep this secret and secure

5. **Bearer Token**: App-only authentication token
   - Found in your app settings
   - Used for enhanced API features

6. **Client ID** (Optional): OAuth 2.0 client ID
   - For newer OAuth 2.0 flows
   - Generate in your app settings

7. **Client Secret** (Optional): OAuth 2.0 client secret
   - For newer OAuth 2.0 flows
   - Keep this secret and secure

## Security Notes

- **Never share your API secrets or tokens publicly**
- **Use environment variables in production deployments**
- **Regularly rotate your access tokens**
- **Monitor your API usage and rate limits**
- **Ensure your apps have only the necessary permissions**

## Testing Your Configuration

Use the "Test Connection" button in the settings page to verify your credentials work correctly before publishing content.

## Getting Help

If you need help obtaining these credentials:
1. Check the platform-specific documentation
2. Look for developer guides on each platform
3. Contact the platform support if credentials aren't working
