"""
Facebook Token Management

This script helps you manage Facebook access tokens including:
1. Converting short-lived tokens to long-lived tokens (60 days)
2. Checking token validity and expiration
3. Auto-renewal warnings
"""

import requests
import json
import yaml
from datetime import datetime, timedelta
import time

class FacebookTokenManager:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        
    def get_long_lived_token(self, short_lived_token):
        """Convert short-lived token to long-lived token (60 days)"""
        print("🔄 Converting to long-lived token...")
        
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': short_lived_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            long_lived_token = data.get('access_token')
            expires_in = data.get('expires_in', 5184000)  # Default 60 days
            
            expiry_date = datetime.now() + timedelta(seconds=expires_in)
            
            print(f"✅ Long-lived token generated!")
            print(f"   Expires in: {expires_in} seconds ({expires_in//86400} days)")
            print(f"   Expiry date: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return {
                'access_token': long_lived_token,
                'expires_in': expires_in,
                'expiry_date': expiry_date.isoformat()
            }
        else:
            print(f"❌ Error generating long-lived token: {response.text}")
            return None
    
    def check_token_validity(self, access_token):
        """Check if token is valid and get expiration info"""
        print("🔍 Checking token validity...")
        
        url = f"https://graph.facebook.com/v18.0/me"
        params = {'access_token': access_token}
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            # Get token debug info
            debug_url = "https://graph.facebook.com/v18.0/debug_token"
            debug_params = {
                'input_token': access_token,
                'access_token': f"{self.app_id}|{self.app_secret}"
            }
            
            debug_response = requests.get(debug_url, params=debug_params)
            
            if debug_response.status_code == 200:
                debug_data = debug_response.json().get('data', {})
                
                is_valid = debug_data.get('is_valid', False)
                expires_at = debug_data.get('expires_at')
                scopes = debug_data.get('scopes', [])
                
                print(f"✅ Token is valid: {is_valid}")
                
                if expires_at:
                    expiry_date = datetime.fromtimestamp(expires_at)
                    days_left = (expiry_date - datetime.now()).days
                    print(f"📅 Expires: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"⏰ Days left: {days_left}")
                    
                    if days_left < 7:
                        print("⚠️  WARNING: Token expires in less than 7 days!")
                    elif days_left < 1:
                        print("🚨 URGENT: Token expires within 24 hours!")
                else:
                    print("📅 Token does not expire (permanent)")
                
                print(f"🔑 Permissions: {', '.join(scopes)}")
                
                return {
                    'is_valid': is_valid,
                    'expires_at': expires_at,
                    'expiry_date': expiry_date.isoformat() if expires_at else None,
                    'days_left': days_left if expires_at else None,
                    'scopes': scopes
                }
            else:
                print(f"❌ Error checking token debug: {debug_response.text}")
                return None
        else:
            print(f"❌ Token is invalid: {response.text}")
            return None
    
    def get_never_expiring_page_token(self, user_access_token, page_id):
        """Get a never-expiring page access token"""
        print("🔄 Getting never-expiring page token...")
        
        # First get long-lived user token
        long_lived_user = self.get_long_lived_token(user_access_token)
        if not long_lived_user:
            return None
        
        # Then get page access token using long-lived user token
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            'fields': 'access_token',
            'access_token': long_lived_user['access_token']
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            page_token = data.get('access_token')
            
            if page_token:
                print("✅ Never-expiring page token generated!")
                print("📌 This token should not expire as long as:")
                print("   - Your app permissions remain valid")
                print("   - You remain admin of the page")
                print("   - Facebook doesn't change their policies")
                
                return page_token
            else:
                print("❌ No page token found in response")
                return None
        else:
            print(f"❌ Error getting page token: {response.text}")
            return None

def manage_facebook_tokens():
    """Interactive Facebook token management"""
    print("📘 FACEBOOK TOKEN MANAGER")
    print("=" * 60)
    
    # Load current config
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        facebook_config = config.get('social_media', {}).get('facebook', {})
        app_id = facebook_config.get('app_id')
        app_secret = facebook_config.get('app_secret')
        current_token = facebook_config.get('access_token')
        page_id = facebook_config.get('page_id')
        
        if not all([app_id, app_secret]):
            print("❌ Missing app_id or app_secret in config")
            return
        
        manager = FacebookTokenManager(app_id, app_secret)
        
        # Check current token
        if current_token:
            print("🔍 Checking current token...")
            token_info = manager.check_token_validity(current_token)
            print()
        
        print("💡 TOKEN RENEWAL OPTIONS:")
        print("1. Generate long-lived token (60 days)")
        print("2. Generate never-expiring page token")
        print("3. Just check current token status")
        print("4. Exit")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            print("\n📋 To get a long-lived token:")
            print("1. Go to https://developers.facebook.com/tools/explorer/")
            print("2. Select your app")
            print("3. Generate a short-lived User Access Token")
            print("4. Enter it below")
            
            short_token = input("\n🔑 Enter short-lived token: ").strip()
            if short_token:
                long_lived = manager.get_long_lived_token(short_token)
                if long_lived:
                    print(f"\n📋 NEW LONG-LIVED TOKEN:")
                    print(f"   {long_lived['access_token']}")
                    print(f"\n💾 Update your config.yaml with this token")
        
        elif choice == "2":
            if not page_id:
                page_id = input("📄 Enter your page ID: ").strip()
            
            print("\n📋 To get a never-expiring page token:")
            print("1. Go to https://developers.facebook.com/tools/explorer/")
            print("2. Select your app")
            print("3. Generate a User Access Token with pages_manage_posts permission")
            print("4. Enter it below")
            
            user_token = input("\n🔑 Enter user access token: ").strip()
            if user_token and page_id:
                page_token = manager.get_never_expiring_page_token(user_token, page_id)
                if page_token:
                    print(f"\n📋 NEVER-EXPIRING PAGE TOKEN:")
                    print(f"   {page_token}")
                    print(f"\n💾 Update your config.yaml with this token")
        
        elif choice == "3":
            if current_token:
                manager.check_token_validity(current_token)
            else:
                print("❌ No token found in config")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    manage_facebook_tokens()
