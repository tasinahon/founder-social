# OAuth Authentication Setup Guide

This guide explains how to set up OAuth authentication for social media platforms in the Founder Socials AI Agent.

## Overview

The agent supports OAuth 2.0 authentication for the following platforms:
- **Twitter/X**: OAuth 2.0 with PKCE (Proof Key for Code Exchange)
- **LinkedIn**: OAuth 2.0
- **Facebook**: OAuth 2.0
- **Instagram**: OAuth 2.0 (via Facebook app)

## Prerequisites

1. **Developer Accounts**: You need developer accounts on the platforms you want to connect
2. **API Credentials**: Client ID and Client Secret from each platform
3. **Redirect URIs**: Configured in your platform apps

## Platform-Specific Setup

### Twitter/X Setup

1. **Create Twitter App**:
   - Go to [Twitter Developer Portal](https://developer.twitter.com)
   - Create a new app or use an existing one
   - Enable OAuth 2.0 with PKCE

2. **Configure App Settings**:
   - **App permissions**: Read and Write
   - **Type of App**: Web App
   - **Callback URLs**: `http://localhost:8000/auth/twitter/callback`
   - **Website URL**: `http://localhost:8000`

3. **Get Credentials**:
   - Copy **Client ID** and **Client Secret**
   - Add to your `config/config.yaml`:
   ```yaml
   api_keys:
     twitter:
       client_id: "your-twitter-client-id"
       client_secret: "your-twitter-client-secret"
   ```

### LinkedIn Setup

1. **Create LinkedIn App**:
   - Go to [LinkedIn Developers](https://www.linkedin.com/developers)
   - Create a new app
   - Request access to Marketing Developer Platform

2. **Configure App Settings**:
   - **OAuth 2.0 settings**:
     - **Redirect URLs**: `http://localhost:8000/auth/linkedin/callback`
     - **Application permissions**: 
       - `r_liteprofile` (Read profile)
       - `r_emailaddress` (Read email)
       - `w_member_social` (Write posts)

3. **Get Credentials**:
   - Copy **Client ID** and **Client Secret**
   - Add to your `config/config.yaml`:
   ```yaml
   api_keys:
     linkedin:
       client_id: "your-linkedin-client-id"
       client_secret: "your-linkedin-client-secret"
   ```

### Facebook Setup

1. **Create Facebook App**:
   - Go to [Facebook Developers](https://developers.facebook.com)
   - Create a new app
   - Add **Facebook Login** product

2. **Configure App Settings**:
   - **Valid OAuth Redirect URIs**: `http://localhost:8000/auth/facebook/callback`
   - **App Domains**: `localhost`
   - **Privacy Policy URL**: (optional for development)

3. **Configure Permissions**:
   - **App Review**: Request permissions for:
     - `pages_manage_posts` (Manage pages)
     - `pages_read_engagement` (Read page insights)
     - `publish_to_groups` (Post to groups)

4. **Get Credentials**:
   - Copy **App ID** and **App Secret**
   - Add to your `config/config.yaml`:
   ```yaml
   api_keys:
     facebook:
       client_id: "your-facebook-app-id"
       client_secret: "your-facebook-app-secret"
   ```

### Instagram Setup

1. **Use Facebook App**:
   - Use the same Facebook app created above
   - Add **Instagram Basic Display** product

2. **Configure Instagram Settings**:
   - **Valid OAuth Redirect URIs**: `http://localhost:8000/auth/instagram/callback`
   - **Deauthorize Callback URL**: (optional)
   - **Data Deletion Request URL**: (optional)

3. **Configure Permissions**:
   - **Basic Display**: Request `basic` permission
   - **Instagram Graph API**: For business accounts

4. **Get Credentials**:
   - Use the same App ID and App Secret from Facebook
   - Add to your `config/config.yaml`:
   ```yaml
   api_keys:
     instagram:
       client_id: "your-facebook-app-id"
       client_secret: "your-facebook-app-secret"
   ```

## Configuration File

Update your `config/config.yaml` with the OAuth credentials:

```yaml
# API Keys for OAuth Authentication
api_keys:
  openai:
    api_key: "your-openai-api-key-here"
  anthropic:
    api_key: "your-anthropic-api-key-here"
  twitter:
    client_id: "your-twitter-client-id"
    client_secret: "your-twitter-client-secret"
  linkedin:
    client_id: "your-linkedin-client-id"
    client_secret: "your-linkedin-client-secret"
  facebook:
    client_id: "your-facebook-client-id"
    client_secret: "your-facebook-client-secret"
  instagram:
    client_id: "your-instagram-client-id"
    client_secret: "your-instagram-client-secret"
```

## Connecting Accounts

1. **Start the Application**:
   ```bash
   python run.py
   ```

2. **Access the Web Interface**:
   - Go to `http://localhost:8000`
   - Navigate to **Settings** → **Social Media Connections**

3. **Connect Platforms**:
   - Click **Connect** for each platform you want to use
   - Complete the OAuth flow in your browser
   - Grant the requested permissions

4. **Verify Connection**:
   - Check that the platform shows as **Connected**
   - View connection details (expiration, scope)

## Security Considerations

1. **Client Secrets**: Never commit client secrets to version control
2. **Redirect URIs**: Use HTTPS in production
3. **Token Storage**: Access tokens are stored in memory (consider persistent storage for production)
4. **Scope**: Request only necessary permissions

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**:
   - Ensure redirect URI exactly matches what's configured in your app
   - Check for trailing slashes or protocol mismatches

2. **"App not configured"**:
   - Verify client ID and client secret are correct
   - Check that the app is properly configured on the platform

3. **"Permission denied"**:
   - Ensure your app has the required permissions
   - For Facebook/Instagram, complete app review process

4. **"Token expired"**:
   - Reconnect the platform to get a new token
   - Implement token refresh logic for production

### Testing

Run the OAuth test script to verify your setup:

```bash
python test_oauth.py
```

This will check:
- Configuration file structure
- API key presence
- Platform configuration status
- Connection status

## Production Deployment

For production deployment:

1. **Use HTTPS**: Update redirect URIs to use HTTPS
2. **Environment Variables**: Store sensitive credentials in environment variables
3. **Token Storage**: Implement secure token storage (database, encrypted files)
4. **Error Handling**: Add comprehensive error handling and logging
5. **Rate Limiting**: Implement rate limiting for OAuth endpoints

## API Endpoints

The OAuth implementation provides these endpoints:

- `GET /auth/{platform}/connect` - Initiate OAuth flow
- `GET /auth/{platform}/callback` - Handle OAuth callback
- `POST /auth/{platform}/disconnect` - Disconnect platform
- `GET /api/auth/status` - Get connection status

## Support

For additional help:
- Check platform-specific documentation
- Review error messages in the application logs
- Test with the provided test script
- Consult platform developer support 