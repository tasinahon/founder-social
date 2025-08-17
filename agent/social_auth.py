"""
Founder Socials AI Agent - Social Media Authentication

Handles OAuth authentication for various social media platforms.
"""

import os
import json
import secrets
import logging
from typing import Dict, Optional, List, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
import requests
from datetime import datetime, timedelta
import base64
import hashlib
import hmac

logger = logging.getLogger(__name__)


class SocialMediaAuth:
    """Handles OAuth authentication for social media platforms."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.oauth_states = {}  # Store OAuth state for security
        self.access_tokens = {}  # Store access tokens
        
        # Platform configurations
        self.platforms = {
            'twitter': {
                'auth_url': 'https://twitter.com/i/oauth2/authorize',
                'token_url': 'https://api.twitter.com/2/oauth2/token',
                'scope': 'tweet.read tweet.write users.read offline.access',
                'redirect_uri': 'http://localhost:8000/auth/twitter/callback'
            },
            'linkedin': {
                'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
                'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
                'scope': 'r_liteprofile r_emailaddress w_member_social',
                'redirect_uri': 'http://localhost:8000/auth/linkedin/callback'
            },
            'facebook': {
                'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
                'scope': 'pages_manage_posts pages_read_engagement publish_to_groups',
                'redirect_uri': 'http://localhost:8000/auth/facebook/callback'
            },
            'instagram': {
                'auth_url': 'https://api.instagram.com/oauth/authorize',
                'token_url': 'https://api.instagram.com/oauth/access_token',
                'scope': 'basic',
                'redirect_uri': 'http://localhost:8000/auth/instagram/callback'
            }
        }
    
    def generate_oauth_state(self) -> str:
        """Generate a secure OAuth state parameter."""
        return secrets.token_urlsafe(32)
    
    def get_auth_url(self, platform: str) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL for a platform.
        
        Returns:
            Tuple of (auth_url, state)
        """
        if platform not in self.platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        
        platform_config = self.platforms[platform]
        api_config = self.config.get('api_keys', {}).get(platform, {})
        
        if not api_config.get('client_id'):
            raise ValueError(f"Missing client_id for {platform}")
        
        # Generate state for security
        state = self.generate_oauth_state()
        self.oauth_states[state] = {
            'platform': platform,
            'timestamp': datetime.now(),
            'used': False
        }
        
        # Build authorization URL
        params = {
            'client_id': api_config['client_id'],
            'redirect_uri': platform_config['redirect_uri'],
            'scope': platform_config['scope'],
            'response_type': 'code',
            'state': state
        }
        
        # Platform-specific parameters
        if platform == 'twitter':
            params['code_challenge'] = self._generate_pkce_challenge()
            params['code_challenge_method'] = 'S256'
        elif platform == 'facebook':
            params['display'] = 'popup'
        
        auth_url = f"{platform_config['auth_url']}?{urlencode(params)}"
        return auth_url, state
    
    def _generate_pkce_challenge(self) -> str:
        """Generate PKCE code challenge for Twitter OAuth."""
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        return code_challenge
    
    async def handle_callback(self, platform: str, code: str, state: str) -> Dict:
        """
        Handle OAuth callback and exchange code for access token.
        
        Returns:
            Dict with authentication result
        """
        # Verify state
        if state not in self.oauth_states:
            raise ValueError("Invalid OAuth state")
        
        oauth_state = self.oauth_states[state]
        if oauth_state['used']:
            raise ValueError("OAuth state already used")
        
        if oauth_state['platform'] != platform:
            raise ValueError("Platform mismatch in OAuth state")
        
        # Mark state as used
        oauth_state['used'] = True
        
        try:
            # Exchange code for access token
            token_data = await self._exchange_code_for_token(platform, code, state)
            
            # Store access token
            self.access_tokens[platform] = {
                'access_token': token_data['access_token'],
                'expires_at': datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600)),
                'refresh_token': token_data.get('refresh_token'),
                'scope': token_data.get('scope', '')
            }
            
            # Get user profile
            profile = await self._get_user_profile(platform, token_data['access_token'])
            
            return {
                'success': True,
                'platform': platform,
                'profile': profile,
                'access_token': token_data['access_token']
            }
            
        except Exception as e:
            logger.error(f"Error handling OAuth callback for {platform}: {e}")
            return {
                'success': False,
                'platform': platform,
                'error': str(e)
            }
    
    async def _exchange_code_for_token(self, platform: str, code: str, state: str) -> Dict:
        """Exchange authorization code for access token."""
        platform_config = self.platforms[platform]
        api_config = self.config.get('api_keys', {}).get(platform, {})
        
        data = {
            'client_id': api_config['client_id'],
            'client_secret': api_config['client_secret'],
            'code': code,
            'redirect_uri': platform_config['redirect_uri'],
            'grant_type': 'authorization_code'
        }
        
        # Platform-specific parameters
        if platform == 'twitter':
            data['code_verifier'] = self._generate_pkce_challenge()
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(platform_config['token_url'], data=data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")
        
        return response.json()
    
    async def _get_user_profile(self, platform: str, access_token: str) -> Dict:
        """Get user profile information from the platform."""
        profile_urls = {
            'twitter': 'https://api.twitter.com/2/users/me',
            'linkedin': 'https://api.linkedin.com/v2/me',
            'facebook': 'https://graph.facebook.com/v18.0/me',
            'instagram': 'https://graph.instagram.com/v18.0/me'
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(profile_urls[platform], headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get profile: {response.text}")
        
        return response.json()
    
    def get_connection_status(self) -> Dict:
        """Get current connection status for all platforms."""
        status = {}
        
        for platform in self.platforms.keys():
            token_info = self.access_tokens.get(platform)
            if token_info:
                # Check if token is expired
                if token_info['expires_at'] > datetime.now():
                    status[platform] = {
                        'connected': True,
                        'expires_at': token_info['expires_at'].isoformat(),
                        'scope': token_info['scope']
                    }
                else:
                    status[platform] = {
                        'connected': False,
                        'reason': 'Token expired'
                    }
            else:
                status[platform] = {
                    'connected': False,
                    'reason': 'Not connected'
                }
        
        return status
    
    def disconnect_platform(self, platform: str) -> bool:
        """Disconnect a platform by removing its access token."""
        if platform in self.access_tokens:
            del self.access_tokens[platform]
            return True
        return False
    
    def get_access_token(self, platform: str) -> Optional[str]:
        """Get access token for a platform if valid."""
        token_info = self.access_tokens.get(platform)
        if token_info and token_info['expires_at'] > datetime.now():
            return token_info['access_token']
        return None
    
    def refresh_token_if_needed(self, platform: str) -> bool:
        """Refresh access token if it's expired and refresh token is available."""
        token_info = self.access_tokens.get(platform)
        if not token_info or not token_info.get('refresh_token'):
            return False
        
        if token_info['expires_at'] <= datetime.now():
            # Implement token refresh logic here
            # This would vary by platform
            logger.warning(f"Token refresh not implemented for {platform}")
            return False
        
        return True


class SocialAuthManager:
    """Manager for social media authentication across the application."""
    
    def __init__(self, config: Dict):
        self.auth = SocialMediaAuth(config)
        self.config = config
    
    def get_platform_config(self, platform: str) -> Dict:
        """Get configuration for a specific platform."""
        return self.config.get('api_keys', {}).get(platform, {})
    
    def is_platform_configured(self, platform: str) -> bool:
        """Check if a platform has the required configuration."""
        config = self.get_platform_config(platform)
        return bool(config.get('client_id') and config.get('client_secret'))
    
    def get_configured_platforms(self) -> List[str]:
        """Get list of platforms that have OAuth configuration."""
        return [
            platform for platform in self.auth.platforms.keys()
            if self.is_platform_configured(platform)
        ]
    
    def get_auth_url(self, platform: str) -> Tuple[str, str]:
        """Get OAuth authorization URL for a platform."""
        if not self.is_platform_configured(platform):
            raise ValueError(f"Platform {platform} is not configured")
        return self.auth.get_auth_url(platform)
    
    async def handle_callback(self, platform: str, code: str, state: str) -> Dict:
        """Handle OAuth callback."""
        return await self.auth.handle_callback(platform, code, state)
    
    def get_connection_status(self) -> Dict:
        """Get connection status for all platforms."""
        return self.auth.get_connection_status()
    
    def disconnect_platform(self, platform: str) -> bool:
        """Disconnect a platform."""
        return self.auth.disconnect_platform(platform)
    
    def get_access_token(self, platform: str) -> Optional[str]:
        """Get access token for a platform."""
        return self.auth.get_access_token(platform) 