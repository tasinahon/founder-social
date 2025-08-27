"""
Integrated Facebook Token Management for Production

This module provides automatic Facebook token management including:
1. Auto-renewal of expiring tokens
2. Token validation before publishing
3. Background token refresh
4. User notification for token issues
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import asyncio
import time

logger = logging.getLogger(__name__)

class FacebookTokenManager:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        
    def check_token_validity(self, access_token: str) -> Dict:
        """Check if token is valid and get expiration info"""
        try:
            # Get token debug info
            debug_url = "https://graph.facebook.com/v18.0/debug_token"
            debug_params = {
                'input_token': access_token,
                'access_token': f"{self.app_id}|{self.app_secret}"
            }
            
            response = requests.get(debug_url, params=debug_params, timeout=30)
            
            if response.status_code == 200:
                debug_data = response.json().get('data', {})
                
                is_valid = debug_data.get('is_valid', False)
                expires_at = debug_data.get('expires_at')
                scopes = debug_data.get('scopes', [])
                
                result = {
                    'is_valid': is_valid,
                    'expires_at': expires_at,
                    'scopes': scopes,
                    'needs_renewal': False,
                    'days_left': None,
                    'expiry_date': None
                }
                
                if expires_at:
                    expiry_date = datetime.fromtimestamp(expires_at)
                    days_left = (expiry_date - datetime.now()).days
                    
                    result.update({
                        'expiry_date': expiry_date.isoformat(),
                        'days_left': days_left,
                        'needs_renewal': days_left < 30  # Renew if less than 30 days
                    })
                    
                    logger.info(f"Facebook token expires in {days_left} days")
                    
                    if days_left < 7:
                        logger.warning(f"Facebook token expires in {days_left} days - renewal needed")
                    elif days_left < 1:
                        logger.error(f"Facebook token expires in {days_left} days - urgent renewal needed")
                
                return result
            else:
                logger.error(f"Error checking Facebook token: {response.text}")
                return {'is_valid': False, 'error': f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Exception checking Facebook token: {e}")
            return {'is_valid': False, 'error': str(e)}
    
    def extend_token_if_needed(self, current_token: str) -> Optional[str]:
        """Automatically extend token if it's expiring soon"""
        try:
            token_info = self.check_token_validity(current_token)
            
            if not token_info.get('is_valid'):
                logger.error("Current Facebook token is invalid")
                return None
            
            if not token_info.get('needs_renewal'):
                logger.info("Facebook token does not need renewal yet")
                return current_token
            
            # Try to extend the token
            logger.info("Attempting to extend Facebook token...")
            extended_token = self.get_long_lived_token(current_token)
            
            if extended_token:
                logger.info("Successfully extended Facebook token")
                return extended_token['access_token']
            else:
                logger.error("Failed to extend Facebook token")
                return None
                
        except Exception as e:
            logger.error(f"Error extending Facebook token: {e}")
            return None
    
    def get_long_lived_token(self, short_lived_token: str) -> Optional[Dict]:
        """Convert short-lived token to long-lived token (60 days)"""
        try:
            url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': short_lived_token
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                long_lived_token = data.get('access_token')
                expires_in = data.get('expires_in', 5184000)  # Default 60 days
                
                expiry_date = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info(f"Generated long-lived Facebook token (expires in {expires_in//86400} days)")
                
                return {
                    'access_token': long_lived_token,
                    'expires_in': expires_in,
                    'expiry_date': expiry_date.isoformat()
                }
            else:
                logger.error(f"Error generating long-lived Facebook token: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception generating long-lived Facebook token: {e}")
            return None
    
    def validate_for_publishing(self, access_token: str, page_id: str) -> Tuple[bool, str]:
        """Validate token and permissions for publishing"""
        try:
            # Check token validity
            token_info = self.check_token_validity(access_token)
            
            if not token_info.get('is_valid'):
                return False, "Facebook access token is invalid or expired. Please update your credentials in Settings."
            
            # Check if token is expiring soon
            days_left = token_info.get('days_left')
            if days_left is not None and days_left < 1:
                return False, f"Facebook access token expires in {days_left} days. Please renew your token in Settings."
            
            # Check required permissions
            scopes = token_info.get('scopes', [])
            required_scopes = ['pages_manage_posts', 'pages_read_engagement']
            missing_scopes = [scope for scope in required_scopes if scope not in scopes]
            
            if missing_scopes:
                return False, f"Facebook token missing permissions: {', '.join(missing_scopes)}. Please re-authorize in Settings."
            
            # Test posting to page
            test_result = self.test_page_posting(access_token, page_id)
            if not test_result[0]:
                return False, test_result[1]
            
            return True, "Facebook credentials are valid and ready for publishing."
            
        except Exception as e:
            logger.error(f"Error validating Facebook credentials: {e}")
            return False, f"Error validating Facebook credentials: {str(e)}"
    
    def test_page_posting(self, access_token: str, page_id: str) -> Tuple[bool, str]:
        """Test if we can post to the page (dry run)"""
        try:
            # Check if page exists and we have access
            url = f"https://graph.facebook.com/v18.0/{page_id}"
            params = {
                'fields': 'id,name,access_token',
                'access_token': access_token
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                page_name = data.get('name', 'Unknown')
                logger.info(f"Successfully accessed Facebook page: {page_name}")
                return True, f"Page access confirmed: {page_name}"
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_message = error_data.get('error', {}).get('message', response.text)
                logger.error(f"Cannot access Facebook page {page_id}: {error_message}")
                return False, f"Cannot access Facebook page: {error_message}"
                
        except Exception as e:
            logger.error(f"Error testing Facebook page access: {e}")
            return False, f"Error testing page access: {str(e)}"


class AutoTokenManager:
    """Automatic token management for production"""
    
    def __init__(self):
        self.token_managers = {}  # Store token managers per user
        self.last_check = {}      # Store last check time per user
        self.check_interval = 3600  # Check every hour
    
    def get_token_manager(self, app_id: str, app_secret: str) -> FacebookTokenManager:
        """Get or create a token manager for given credentials"""
        key = f"{app_id}:{app_secret}"
        if key not in self.token_managers:
            self.token_managers[key] = FacebookTokenManager(app_id, app_secret)
        return self.token_managers[key]
    
    def should_check_token(self, user_email: str) -> bool:
        """Check if it's time to validate the token for this user"""
        last_check = self.last_check.get(user_email, 0)
        return (time.time() - last_check) > self.check_interval
    
    def check_and_refresh_token(self, user_email: str, facebook_config: Dict) -> Dict:
        """Check token and refresh if needed"""
        try:
            app_id = facebook_config.get('app_id')
            app_secret = facebook_config.get('app_secret')
            access_token = facebook_config.get('access_token')
            page_id = facebook_config.get('page_id')
            
            if not all([app_id, app_secret, access_token, page_id]):
                return {
                    'success': False,
                    'error': 'Missing Facebook credentials',
                    'needs_setup': True
                }
            
            token_manager = self.get_token_manager(app_id, app_secret)
            
            # Check if token needs renewal
            extended_token = token_manager.extend_token_if_needed(access_token)
            
            if extended_token and extended_token != access_token:
                # Token was renewed - we need to save this back to user settings
                logger.info(f"Facebook token renewed for user {user_email}")
                facebook_config['access_token'] = extended_token
                
                # TODO: Update user settings with new token
                # This would need to be integrated with the user_settings_manager
                
            # Validate for publishing
            is_valid, message = token_manager.validate_for_publishing(
                extended_token or access_token, page_id
            )
            
            self.last_check[user_email] = time.time()
            
            return {
                'success': is_valid,
                'message': message,
                'token_renewed': extended_token != access_token if extended_token else False,
                'new_token': extended_token if extended_token != access_token else None
            }
            
        except Exception as e:
            logger.error(f"Error checking Facebook token for {user_email}: {e}")
            return {
                'success': False,
                'error': str(e),
                'needs_manual_intervention': True
            }
    
    async def background_token_check(self, user_settings_manager):
        """Background task to check and renew tokens for all users"""
        logger.info("Starting background Facebook token check...")
        
        try:
            # Get all users with Facebook configured
            # This would need integration with the user management system
            users_with_facebook = []  # TODO: Implement getting users with Facebook
            
            for user_email in users_with_facebook:
                try:
                    if self.should_check_token(user_email):
                        user_config = user_settings_manager.get_platform_settings(user_email, 'facebook')
                        if user_config and user_config.get('enabled'):
                            result = self.check_and_refresh_token(user_email, user_config)
                            
                            if result.get('token_renewed'):
                                # Save the new token
                                user_config['access_token'] = result['new_token']
                                user_settings_manager.save_platform_settings(
                                    user_email, 'facebook', user_config
                                )
                                logger.info(f"Updated Facebook token for user {user_email}")
                            
                            if not result['success']:
                                logger.warning(f"Facebook token issue for {user_email}: {result.get('message')}")
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error checking Facebook token for {user_email}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in background Facebook token check: {e}")
        
        logger.info("Completed background Facebook token check")


# Global instance for production use
auto_token_manager = AutoTokenManager()


def validate_facebook_credentials(user_email: str, facebook_config: Dict) -> Tuple[bool, str]:
    """Production function to validate Facebook credentials before publishing"""
    try:
        result = auto_token_manager.check_and_refresh_token(user_email, facebook_config)
        
        if result.get('needs_setup'):
            return False, "Facebook credentials not configured. Please set up your Facebook credentials in Settings."
        
        if result.get('needs_manual_intervention'):
            return False, f"Facebook token requires manual renewal. Please update your credentials in Settings. Error: {result.get('error', 'Unknown error')}"
        
        return result['success'], result['message']
        
    except Exception as e:
        logger.error(f"Error validating Facebook credentials for {user_email}: {e}")
        return False, f"Error validating Facebook credentials: {str(e)}"
