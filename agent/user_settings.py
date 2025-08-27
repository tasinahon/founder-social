"""
User Settings Manager
Handles per-user configuration storage and retrieval
"""

import os
import json
import sqlite3
import logging
from typing import Dict, Any, Optional
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

class UserSettingsManager:
    def __init__(self, db_path: str = "./data/user_settings.db"):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Create the user settings database if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create user_settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                platform TEXT,
                settings_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, category, platform)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_or_create_user(self, email: str, name: str = None) -> int:
        """Get user ID or create new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Try to get existing user
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
        else:
            # Create new user
            cursor.execute(
                'INSERT INTO users (email, name) VALUES (?, ?)',
                (email, name)
            )
            user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return user_id
    
    def save_platform_settings(self, user_email: str, platform: str, settings: Dict[str, Any]) -> bool:
        """Save platform-specific settings for a user"""
        try:
            user_id = self.get_or_create_user(user_email)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            settings_json = json.dumps(settings)
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_settings 
                (user_id, category, platform, settings_json, updated_at)
                VALUES (?, 'social_media', ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, platform, settings_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving platform settings: {e}")
            return False
    
    def save_startup_settings(self, user_email: str, settings: Dict[str, Any]) -> bool:
        """Save startup information for a user"""
        try:
            user_id = self.get_or_create_user(user_email)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            settings_json = json.dumps(settings)
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_settings 
                (user_id, category, settings_json, updated_at)
                VALUES (?, 'startup', ?, CURRENT_TIMESTAMP)
            ''', (user_id, settings_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving startup settings: {e}")
            return False
    
    def get_platform_settings(self, user_email: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get platform-specific settings for a user"""
        try:
            user_id = self.get_or_create_user(user_email)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT settings_json FROM user_settings 
                WHERE user_id = ? AND category = 'social_media' AND platform = ?
            ''', (user_id, platform))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            print(f"Error getting platform settings: {e}")
            return None
    
    def get_startup_settings(self, user_email: str) -> Optional[Dict[str, Any]]:
        """Get startup settings for a user"""
        try:
            user_id = self.get_or_create_user(user_email)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT settings_json FROM user_settings 
                WHERE user_id = ? AND category = 'startup'
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            print(f"Error getting startup settings: {e}")
            return None
    
    def get_all_user_settings(self, user_email: str) -> Dict[str, Any]:
        """Get all settings for a user"""
        try:
            user_id = self.get_or_create_user(user_email)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT category, platform, settings_json FROM user_settings 
                WHERE user_id = ?
            ''', (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            settings = {
                'platforms': {},
                'startup': {}
            }
            
            for category, platform, settings_json in results:
                data = json.loads(settings_json)
                if category == 'social_media':
                    settings['platforms'][platform] = data
                elif category == 'startup':
                    settings['startup'] = data
            
            return settings
        except Exception as e:
            print(f"Error getting all user settings: {e}")
            return {'platforms': {}, 'startup': {}}
    
    def generate_user_config(self, user_email: str) -> Dict[str, Any]:
        """Generate a complete config for a user by merging default config with user settings"""
        try:
            # Load default config
            default_config_path = Path("config/config.yaml")
            if default_config_path.exists():
                with open(default_config_path, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                config = self._get_default_config()
            
            # Get user settings
            user_settings = self.get_all_user_settings(user_email)
            
            # Override with user-specific settings
            if user_settings['startup']:
                config['startup'].update(user_settings['startup'])
            
            if user_settings['platforms']:
                for platform, settings in user_settings['platforms'].items():
                    if platform in config['social_media']:
                        config['social_media'][platform].update(settings['config'])
                        config['social_media'][platform]['enabled'] = settings['enabled']
            
            return config
        except Exception as e:
            print(f"Error generating user config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure"""
        return {
            'startup': {
                'name': 'Your Startup Name',
                'description': 'Brief description of your startup',
                'industry': 'Technology',
                'website': 'https://yourstartup.com'
            },
            'social_media': {
                'facebook': {
                    'enabled': False,
                    'access_token': '',
                    'app_id': '',
                    'app_secret': '',
                    'page_id': '',
                    'auto_post': True
                },
                'linkedin': {
                    'enabled': False,
                    'access_token': '',
                    'client_id': '',
                    'client_secret': '',
                    'company_id': '',
                    'posting_mode': 'personal',
                    'auto_post': True
                },
                'twitter': {
                    'enabled': False,
                    'api_key': '',
                    'api_secret': '',
                    'access_token': '',
                    'access_token_secret': '',
                    'bearer_token': '',
                    'client_id': '',
                    'client_secret': '',
                    'auto_post': True
                }
            },
            'ai': {
                'provider': 'gemini',
                'gemini': {
                    'api_key': 'AIzaSyCmbCRGsCfd_xJxKoiEouyeTYSIi6WppzE',
                    'model': 'gemini-1.5-flash',
                    'temperature': 0.7
                }
            }
        }
    
    def test_platform_connection(self, platform: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection to a platform with given configuration"""
        try:
            if platform == 'facebook':
                return self._test_facebook_connection(config)
            elif platform == 'linkedin':
                return self._test_linkedin_connection(config)
            elif platform == 'twitter':
                return self._test_twitter_connection(config)
            else:
                return {'success': False, 'error': 'Unsupported platform'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_facebook_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Facebook API connection"""
        import requests
        
        access_token = config.get('access_token')
        if not access_token:
            return {'success': False, 'error': 'Access token is required'}
        
        try:
            # Test API call to get page info
            response = requests.get(
                f'https://graph.facebook.com/v18.0/me?access_token={access_token}'
            )
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Facebook connection successful'}
            else:
                error_data = response.json()
                return {'success': False, 'error': error_data.get('error', {}).get('message', 'Invalid access token')}
        except Exception as e:
            return {'success': False, 'error': f'Connection failed: {str(e)}'}
    
    def _test_linkedin_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test LinkedIn API connection"""
        import requests
        
        access_token = config.get('access_token')
        if not access_token:
            return {'success': False, 'error': 'Access token is required'}
        
        try:
            # Test API call to get user profile
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                'https://api.linkedin.com/v2/me',
                headers=headers
            )
            
            if response.status_code == 200:
                return {'success': True, 'message': 'LinkedIn connection successful'}
            else:
                return {'success': False, 'error': 'Invalid access token or expired'}
        except Exception as e:
            return {'success': False, 'error': f'Connection failed: {str(e)}'}
    
    def _test_twitter_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Twitter API connection"""
        import requests
        
        bearer_token = config.get('bearer_token')
        if not bearer_token:
            return {'success': False, 'error': 'Bearer token is required'}
        
        try:
            # Test API call to get user profile
            headers = {'Authorization': f'Bearer {bearer_token}'}
            response = requests.get(
                'https://api.twitter.com/2/users/me',
                headers=headers
            )
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Twitter connection successful'}
            else:
                return {'success': False, 'error': 'Invalid bearer token or expired'}
        except Exception as e:
            return {'success': False, 'error': f'Connection failed: {str(e)}'}
    
    def check_user_platform_credentials(self, user_email: str, platform: str) -> dict:
        """Check if user has configured credentials for a specific platform"""
        try:
            settings = self.get_platform_settings(user_email, platform)
            
            if not settings:
                return {
                    "configured": False,
                    "enabled": False,
                    "message": f"No {platform} credentials configured. Please set up your {platform} credentials in Settings.",
                    "missing_fields": self._get_required_fields(platform)
                }
            
            enabled = settings.get('enabled', False)
            config = settings.get('config', {})
            required_fields = self._get_required_fields(platform)
            missing_fields = []
            
            for field in required_fields:
                if not config.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    "configured": False,
                    "enabled": enabled,
                    "message": f"Missing {platform} credentials: {', '.join(missing_fields)}. Please complete your {platform} setup in Settings.",
                    "missing_fields": missing_fields
                }
            
            if not enabled:
                return {
                    "configured": True,
                    "enabled": False,
                    "message": f"{platform} is configured but disabled. Please enable {platform} publishing in Settings.",
                    "missing_fields": []
                }
            
            return {
                "configured": True,
                "enabled": True,
                "message": f"{platform} is ready for publishing.",
                "missing_fields": []
            }
            
        except Exception as e:
            logger.error(f"Error checking {platform} credentials for {user_email}: {e}")
            return {
                "configured": False,
                "enabled": False,
                "message": f"Error checking {platform} credentials: {str(e)}",
                "missing_fields": []
            }
    
    def _get_required_fields(self, platform: str) -> list:
        """Get required fields for a platform"""
        required_fields = {
            'facebook': ['app_id', 'app_secret', 'access_token', 'page_id'],
            'linkedin': ['client_id', 'client_secret', 'access_token'],
            'twitter': ['api_key', 'api_secret', 'access_token', 'access_token_secret']
        }
        return required_fields.get(platform, [])
    
    def check_multiple_platforms(self, user_email: str, platforms: list) -> dict:
        """Check credentials for multiple platforms and return detailed status"""
        results = {}
        ready_platforms = []
        issues = []
        
        for platform in platforms:
            check_result = self.check_user_platform_credentials(user_email, platform)
            results[platform] = check_result
            
            if check_result['configured'] and check_result['enabled']:
                ready_platforms.append(platform)
            else:
                issues.append({
                    'platform': platform,
                    'message': check_result['message'],
                    'missing_fields': check_result['missing_fields']
                })
        
        return {
            'ready_platforms': ready_platforms,
            'issues': issues,
            'can_publish': len(ready_platforms) > 0,
            'all_ready': len(issues) == 0,
            'details': results
        }


# Global instance
user_settings_manager = UserSettingsManager()
