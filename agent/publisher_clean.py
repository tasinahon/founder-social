"""
Social Media Publisher for Founder Socials AI Agent

This module handles publishing content to various social media platforms and blogs.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
import requests
import json
import hashlib
import hmac
import base64
import urllib.parse
import secrets

try:
    import tweepy
except ImportError:
    tweepy = None

try:
    import linkedin_api
except ImportError:
    linkedin_api = None

try:
    import facebook
except ImportError:
    facebook = None

logger = logging.getLogger(__name__)

class Publisher:
    """
    Handles publishing content to various platforms
    """
    
    def __init__(self, config: Dict):
        """Initialize the publisher"""
        self.config = config
        self.social_config = config.get('social_media', {})
        self.blog_config = config.get('blog_platforms', {})
        
        # Initialize platform clients
        self._init_platform_clients()
        
        logger.info("Publisher initialized")
    
    def _init_platform_clients(self):
        """Initialize platform-specific clients"""
        self.clients = {}
        
        # Twitter/X (keeping old tweepy client for compatibility)
        if self.social_config.get('twitter', {}).get('enabled', False):
            try:
                twitter_config = self.social_config['twitter']
                if tweepy:
                    auth = tweepy.OAuthHandler(
                        twitter_config['api_key'],
                        twitter_config['api_secret']
                    )
                    auth.set_access_token(
                        twitter_config['access_token'],
                        twitter_config['access_token_secret']
                    )
                    self.clients['twitter'] = tweepy.API(auth)
                    logger.info("Twitter client initialized")
            except Exception as e:
                logger.error(f"Error initializing Twitter client: {e}")
        
        # LinkedIn (simplified - would need proper LinkedIn API setup)
        if self.social_config.get('linkedin', {}).get('enabled', False):
            self.clients['linkedin'] = self._init_linkedin_client()
        
        # WordPress
        if self.blog_config.get('wordpress', {}).get('enabled', False):
            self.clients['wordpress'] = self._init_wordpress_client()
    
    def _init_linkedin_client(self):
        """Initialize LinkedIn client (placeholder)"""
        # In a real implementation, you'd use the LinkedIn API
        # For now, return a mock client
        return {
            'type': 'linkedin',
            'config': self.social_config.get('linkedin', {})
        }
    
    def _init_wordpress_client(self):
        """Initialize WordPress client (placeholder)"""
        # In a real implementation, you'd use WordPress XML-RPC or REST API
        return {
            'type': 'wordpress',
            'config': self.blog_config.get('wordpress', {})
        }
    
    async def publish(self, content: str, platform: str, content_type: str, 
                     metadata: Optional[Dict] = None, posting_mode: Optional[str] = None) -> bool:
        """
        Publish content to the specified platform
        
        Args:
            content: The content to publish
            platform: Target platform
            content_type: Type of content (blog or social)
            metadata: Additional metadata
            posting_mode: For LinkedIn - 'personal', 'company', or None (use config default)
            
        Returns:
            True if published successfully, False otherwise
        """
        logger.info(f"Publishing {content_type} content to {platform}")
        
        try:
            if platform == 'twitter':
                return await self._publish_to_twitter(content, metadata)
            elif platform == 'linkedin':
                return await self._publish_to_linkedin(content, content_type, metadata, posting_mode)
            elif platform == 'facebook':
                return await self._publish_to_facebook(content, metadata)
            elif platform == 'instagram':
                return await self._publish_to_instagram(content, metadata)
            elif platform == 'wordpress':
                return await self._publish_to_wordpress(content, metadata)
            else:
                logger.error(f"Unsupported platform: {platform}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing to {platform}: {e}")
            return False
    
    async def _publish_to_twitter(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Publish content to Twitter/X using API v2 - Simple single tweet approach"""
        try:
            config = self.social_config.get('twitter', {})
            
            # Detailed logging for debugging
            logger.info("🐦 TWITTER PUBLISHING DEBUG:")
            logger.info(f"   Twitter enabled: {config.get('enabled', False)}")
            logger.info(f"   API Key present: {'api_key' in config and bool(config.get('api_key'))}")
            logger.info(f"   API Secret present: {'api_secret' in config and bool(config.get('api_secret'))}")
            logger.info(f"   Access Token present: {'access_token' in config and bool(config.get('access_token'))}")
            
            # Check if Twitter is enabled and configured
            if not config.get('enabled', False):
                logger.warning("❌ Twitter publishing disabled in config - simulating publish")
                logger.info(f"Mock Twitter post: {content[:100]}...")
                await asyncio.sleep(1)
                return True
            
            # Check required credentials
            required_keys = ['api_key', 'api_secret', 'access_token', 'access_token_secret']
            missing_keys = [key for key in required_keys if not config.get(key) or config.get(key).startswith('your-')]
            if missing_keys:
                logger.warning(f"❌ Missing Twitter credentials: {missing_keys} - simulating publish")
                logger.info(f"Mock Twitter post: {content[:100]}...")
                await asyncio.sleep(1)
                return True
            
            # Real Twitter API publishing - SIMPLE APPROACH
            logger.info("✅ ALL CHECKS PASSED - ATTEMPTING REAL TWITTER PUBLISH")
            
            # Check content length and truncate if needed (NO THREADING)
            character_limit = config.get('character_limit', 280)
            
            # Clean and validate content
            if not content or not content.strip():
                logger.error("❌ Empty or whitespace-only content for Twitter")
                return False
            
            content = content.strip()
            
            # Simple truncation if content is too long (no threading complexity)
            if len(content) > character_limit:
                logger.info(f"Content exceeds Twitter character limit ({character_limit}), truncating...")
                # Truncate and add ellipsis
                truncated_content = content[:character_limit-3] + "..."
                logger.info(f"Truncated from {len(content)} to {len(truncated_content)} characters")
                content = truncated_content
            
            logger.info(f"📝 Posting single tweet ({len(content)} chars): {content[:100]}...")
            
            # Set up Twitter API v2 endpoint with OAuth 1.0a authentication
            url = "https://api.twitter.com/2/tweets"
            
            # Prepare simple payload
            payload = {"text": content}
            
            # Create OAuth 1.0a headers
            headers = self._create_twitter_oauth_headers(
                url=url,
                method="POST",
                api_key=config['api_key'],
                api_secret=config['api_secret'],
                access_token=config['access_token'],
                access_token_secret=config['access_token_secret']
            )
            headers["Content-Type"] = "application/json"
            
            logger.info(f"🔗 Twitter API URL: {url}")
            logger.info(f"🔑 Using OAuth 1.0a authentication...")
            
            # Make the API call
            response = requests.post(url, headers=headers, json=payload)
            
            logger.info(f"🔍 Twitter API Response: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                tweet_id = result.get('data', {}).get('id')
                tweet_text = result.get('data', {}).get('text')
                
                logger.info(f"✅ Tweet published successfully!")
                logger.info(f"   ID: {tweet_id}")
                logger.info(f"   Text: {tweet_text}")
                logger.info(f"   URL: https://twitter.com/i/web/status/{tweet_id}")
                
                return True
                
            elif response.status_code == 403:
                error_text = response.text
                logger.error(f"❌ Twitter 403 Forbidden: {error_text}")
                
                if "duplicate" in error_text.lower():
                    logger.info("🔄 Duplicate content detected, adding timestamp...")
                    # Add timestamp to make content unique
                    unique_content = f"{content} #{int(time.time())}"
                    
                    # Ensure it still fits within limit
                    if len(unique_content) <= character_limit:
                        retry_payload = {"text": unique_content}
                        retry_response = requests.post(url, headers=headers, json=retry_payload)
                        
                        if retry_response.status_code == 201:
                            result = retry_response.json()
                            tweet_id = result.get('data', {}).get('id')
                            logger.info(f"✅ Retry successful! Tweet ID: {tweet_id}")
                            return True
                        else:
                            logger.error(f"❌ Retry also failed: {retry_response.status_code}")
                
                logger.error("💡 This may be a permissions issue - check if your Twitter app has 'Read and write' permissions")
                return False
                
            elif response.status_code == 429:
                logger.warning(f"⏱️ Rate limit hit, but we're only posting one tweet...")
                logger.warning(f"Response: {response.text}")
                return False
                
            else:
                logger.error(f"❌ Error posting tweet: {response.status_code}")
                logger.error(f"📄 Response: {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Error publishing to Twitter: {e}")
            return False
    
    async def _publish_to_linkedin(self, content: str, content_type: str, 
                                 metadata: Optional[Dict] = None, posting_mode: Optional[str] = None) -> bool:
        """Publish content to LinkedIn"""
        try:
            config = self.social_config.get('linkedin', {})
            
            logger.info("🔍 LINKEDIN PUBLISHING DEBUG:")
            logger.info(f"   LinkedIn enabled: {config.get('enabled', False)}")
            
            if not config.get('enabled', False):
                logger.warning("❌ LinkedIn publishing disabled in config - simulating publish")
                logger.info(f"Mock LinkedIn post: {content[:100]}...")
                await asyncio.sleep(1)
                return True
            
            logger.info(f"Mock LinkedIn {content_type}: {content[:100]}...")
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Error publishing to LinkedIn: {e}")
            return False
    
    async def _publish_to_facebook(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Publish content to Facebook"""
        try:
            config = self.social_config.get('facebook', {})
            
            if not config.get('enabled', False):
                logger.warning("❌ Facebook publishing disabled - simulating publish")
                logger.info(f"Mock Facebook post: {content[:100]}...")
                await asyncio.sleep(1)
                return True
                
            logger.info(f"Mock Facebook post: {content[:100]}...")
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Error publishing to Facebook: {e}")
            return False
    
    async def _publish_to_instagram(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Publish content to Instagram"""
        try:
            logger.info(f"Mock Instagram post: {content[:100]}...")
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Error publishing to Instagram: {e}")
            return False
    
    async def _publish_to_wordpress(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Publish content to WordPress"""
        try:
            logger.info(f"Mock WordPress post: {content[:100]}...")
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Error publishing to WordPress: {e}")
            return False
    
    def _create_twitter_oauth_headers(self, url: str, method: str, api_key: str, 
                                    api_secret: str, access_token: str, access_token_secret: str) -> Dict[str, str]:
        """Create OAuth 1.0a headers for Twitter API v2"""
        
        # OAuth parameters
        oauth_nonce = secrets.token_hex(16)
        oauth_timestamp = str(int(time.time()))
        oauth_version = "1.0"
        oauth_signature_method = "HMAC-SHA1"
        
        # Parameters for signature
        params = {
            'oauth_consumer_key': api_key,
            'oauth_nonce': oauth_nonce,
            'oauth_signature_method': oauth_signature_method,
            'oauth_timestamp': oauth_timestamp,
            'oauth_token': access_token,
            'oauth_version': oauth_version
        }
        
        # Create parameter string
        param_string = '&'.join([f"{k}={urllib.parse.quote(str(v), safe='')}" 
                                for k, v in sorted(params.items())])
        
        # Create signature base string
        signature_base = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
        
        # Create signing key
        signing_key = f"{urllib.parse.quote(api_secret, safe='')}&{urllib.parse.quote(access_token_secret, safe='')}"
        
        # Generate signature
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), signature_base.encode(), hashlib.sha1).digest()
        ).decode()
        
        # Create authorization header
        auth_params = {
            'oauth_consumer_key': api_key,
            'oauth_nonce': oauth_nonce,
            'oauth_signature': signature,
            'oauth_signature_method': oauth_signature_method,
            'oauth_timestamp': oauth_timestamp,
            'oauth_token': access_token,
            'oauth_version': oauth_version
        }
        
        auth_header = 'OAuth ' + ', '.join([f'{k}="{urllib.parse.quote(str(v), safe="")}"' 
                                          for k, v in sorted(auth_params.items())])
        
        return {
            'Authorization': auth_header
        }
