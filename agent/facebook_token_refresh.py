"""
Automatic Facebook Token Refresh System

This module adds automatic token refresh capabilities to the publisher
"""

import json
import os
from datetime import datetime, timedelta
import logging

class FacebookTokenRefresh:
    def __init__(self, config):
        self.config = config
        self.app_id = config.get('app_id')
        self.app_secret = config.get('app_secret')
        self.token_file = 'data/facebook_token_info.json'
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
    
    def save_token_info(self, token, expires_at=None):
        """Save token with expiration info"""
        token_info = {
            'access_token': token,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at,
            'last_checked': datetime.now().isoformat()
        }
        
        with open(self.token_file, 'w') as f:
            json.dump(token_info, f, indent=2)
        
        print(f"💾 Token info saved to {self.token_file}")
    
    def load_token_info(self):
        """Load token info from file"""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                return json.load(f)
        return None
    
    def is_token_expiring_soon(self, days_warning=7):
        """Check if token expires soon"""
        token_info = self.load_token_info()
        if not token_info or not token_info.get('expires_at'):
            return False
        
        expires_at = datetime.fromisoformat(token_info['expires_at'])
        days_left = (expires_at - datetime.now()).days
        
        return days_left <= days_warning
    
    def get_valid_token(self):
        """Get a valid token, refresh if needed"""
        token_info = self.load_token_info()
        
        if not token_info:
            # No saved token info, return current config token
            current_token = self.config.get('access_token')
            if current_token:
                print("⚠️  No token expiration info found. Consider running token manager.")
                return current_token
            return None
        
        # Check if token is expiring soon
        if self.is_token_expiring_soon():
            print("⚠️  Facebook token expires soon! Please run facebook_token_manager.py")
            
        return token_info.get('access_token')
    
    def check_and_warn(self):
        """Check token status and warn if needed"""
        if self.is_token_expiring_soon(days_warning=7):
            print("🚨 WARNING: Facebook token expires in less than 7 days!")
            print("   Run: python facebook_token_manager.py")
            return False
        
        if self.is_token_expiring_soon(days_warning=1):
            print("🚨 URGENT: Facebook token expires within 24 hours!")
            print("   Run: python facebook_token_manager.py")
            return False
        
        return True

# Add this to your publisher.py
def get_facebook_token_with_refresh(config):
    """Get Facebook token with automatic refresh warning"""
    refresh_manager = FacebookTokenRefresh(config)
    
    # Check token status
    if not refresh_manager.check_and_warn():
        print("⚠️  Proceeding with potentially expired token...")
    
    # Get valid token
    token = refresh_manager.get_valid_token()
    
    if not token:
        token = config.get('access_token')
        print("⚠️  Using fallback token from config")
    
    return token
