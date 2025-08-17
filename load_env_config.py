#!/usr/bin/env python3
"""
Environment Configuration Loader
Loads environment variables and creates/updates config.yaml
"""

import os
import yaml
from pathlib import Path

def load_config_from_env():
    """Load configuration from environment variables"""
    
    config = {
        'ai': {
            'provider': os.getenv('AI_PROVIDER', 'gpt4o'),
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here'),
                'model': os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
                'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            },
            'azure_openai': {
                'api_key': os.getenv('AZURE_OPENAI_API_KEY', 'your-azure-openai-api-key-here'),
                'azure_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT', 'https://your-resource.openai.azure.com/'),
                'model': os.getenv('AZURE_OPENAI_MODEL', 'gpt-4-turbo-preview'),
                'api_version': os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview'),
                'temperature': float(os.getenv('AZURE_OPENAI_TEMPERATURE', '0.7'))
            },
            'deepseek_r1': {
                'api_key': os.getenv('DEEPSEEK_R1_API_KEY', 'your-deepseek-api-key-here'),
                'azure_endpoint': os.getenv('DEEPSEEK_R1_ENDPOINT', 'https://your-resource.openai.azure.com/'),
                'api_version': os.getenv('DEEPSEEK_R1_API_VERSION', '2024-12-01-preview'),
                'temperature': float(os.getenv('DEEPSEEK_R1_TEMPERATURE', '0.7'))
            },
            'gpt4o': {
                'api_key': os.getenv('GPT4O_API_KEY', 'your-gpt4o-api-key-here'),
                'endpoint': os.getenv('GPT4O_ENDPOINT', 'https://your-resource.openai.azure.com/openai/deployments/gpt-4o'),
                'temperature': float(os.getenv('GPT4O_TEMPERATURE', '0.7'))
            }
        },
        
        'api_keys': {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
            },
            'azure_openai': {
                'api_key': os.getenv('AZURE_OPENAI_API_KEY', 'your-azure-openai-api-key-here'),
                'azure_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT', 'https://your-resource.openai.azure.com/')
            },
            'deepseek_r1': {
                'api_key': os.getenv('DEEPSEEK_R1_API_KEY', 'your-deepseek-api-key-here'),
                'azure_endpoint': os.getenv('DEEPSEEK_R1_ENDPOINT', 'https://your-resource.openai.azure.com/')
            },
            'gpt4o': {
                'api_key': os.getenv('GPT4O_API_KEY', 'your-gpt4o-api-key-here'),
                'endpoint': os.getenv('GPT4O_ENDPOINT', 'https://your-resource.openai.azure.com/openai/deployments/gpt-4o')
            },
            'twitter': {
                'client_id': os.getenv('TWITTER_CLIENT_ID', 'your-twitter-client-id'),
                'client_secret': os.getenv('TWITTER_CLIENT_SECRET', 'your-twitter-client-secret')
            },
            'facebook': {
                'client_id': os.getenv('FACEBOOK_CLIENT_ID', 'your-facebook-client-id'),
                'client_secret': os.getenv('FACEBOOK_CLIENT_SECRET', 'your-facebook-client-secret')
            },
            'linkedin': {
                'client_id': os.getenv('LINKEDIN_CLIENT_ID', 'your-linkedin-client-id'),
                'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET', 'your-linkedin-client-secret')
            },
            'instagram': {
                'client_id': os.getenv('INSTAGRAM_CLIENT_ID', 'your-instagram-client-id'),
                'client_secret': os.getenv('INSTAGRAM_CLIENT_SECRET', 'your-instagram-client-secret')
            }
        },
        
        'social_media': {
            'twitter': {
                'enabled': True,
                'auto_post': True,
                'character_limit': 280,
                'client_id': os.getenv('TWITTER_CLIENT_ID', 'your-twitter-client-id'),
                'client_secret': os.getenv('TWITTER_CLIENT_SECRET', 'your-twitter-client-secret'),
                'api_key': os.getenv('TWITTER_API_KEY', 'your-twitter-api-key'),
                'api_secret': os.getenv('TWITTER_API_SECRET', 'your-twitter-api-secret'),
                'access_token': os.getenv('TWITTER_ACCESS_TOKEN', 'your-twitter-access-token'),
                'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET', 'your-twitter-access-token-secret'),
                'bearer_token': os.getenv('TWITTER_BEARER_TOKEN', 'your-twitter-bearer-token')
            },
            'facebook': {
                'enabled': True,
                'auto_post': True,
                'app_id': os.getenv('FACEBOOK_APP_ID', 'your-facebook-app-id'),
                'app_secret': os.getenv('FACEBOOK_APP_SECRET', 'your-facebook-app-secret'),
                'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', 'your-facebook-access-token'),
                'page_id': os.getenv('FACEBOOK_PAGE_ID', 'your-facebook-page-id')
            },
            'linkedin': {
                'enabled': True,
                'auto_post': True,
                'client_id': os.getenv('LINKEDIN_CLIENT_ID', 'your-linkedin-client-id'),
                'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET', 'your-linkedin-client-secret'),
                'access_token': os.getenv('LINKEDIN_ACCESS_TOKEN', 'your-linkedin-access-token'),
                'company_id': os.getenv('LINKEDIN_COMPANY_ID', 'your-linkedin-company-id'),
                'company_name': os.getenv('LINKEDIN_COMPANY_NAME', 'Your Company'),
                'posting_mode': 'company'
            },
            'instagram': {
                'enabled': False,
                'auto_post': False,
                'username': os.getenv('INSTAGRAM_USERNAME', 'your-instagram-username'),
                'password': os.getenv('INSTAGRAM_PASSWORD', 'your-instagram-password')
            }
        },
        
        'blog_platforms': {
            'wordpress': {
                'enabled': True,
                'auto_post': True,
                'url': os.getenv('WORDPRESS_URL', 'https://yourstartup.com'),
                'username': os.getenv('WORDPRESS_USERNAME', 'your-wordpress-username'),
                'password': os.getenv('WORDPRESS_PASSWORD', 'your-wordpress-password')
            },
            'medium': {
                'enabled': False,
                'auto_post': False,
                'access_token': os.getenv('MEDIUM_ACCESS_TOKEN', 'your-medium-access-token')
            },
            'ghost': {
                'enabled': False,
                'auto_post': False,
                'url': os.getenv('GHOST_URL', 'https://your-ghost-blog.com'),
                'api_key': os.getenv('GHOST_API_KEY', 'your-ghost-api-key')
            }
        },
        
        'analytics': {
            'google_analytics': {
                'enabled': False,
                'tracking_id': os.getenv('GOOGLE_ANALYTICS_TRACKING_ID', 'GA-XXXXXXXXX-X'),
                'credentials_file': os.getenv('GOOGLE_ANALYTICS_CREDENTIALS_FILE', 'path/to/credentials.json')
            },
            'google_search_console': {
                'enabled': False,
                'site_url': os.getenv('GOOGLE_SEARCH_CONSOLE_SITE_URL', 'https://yourstartup.com'),
                'credentials_file': os.getenv('GOOGLE_SEARCH_CONSOLE_CREDENTIALS_FILE', 'path/to/credentials.json')
            }
        },
        
        'startup': {
            'name': os.getenv('STARTUP_NAME', 'Your Startup Name'),
            'description': os.getenv('STARTUP_DESCRIPTION', 'Brief description of your startup and what you do'),
            'industry': os.getenv('STARTUP_INDUSTRY', 'Technology'),
            'website': os.getenv('STARTUP_WEBSITE', 'https://yourstartup.com'),
            'blog_url': os.getenv('STARTUP_BLOG_URL', 'https://yourstartup.com/blog'),
            'target_audience': os.getenv('STARTUP_TARGET_AUDIENCE', 'Startup founders, tech professionals, entrepreneurs'),
            'brand_voice': os.getenv('STARTUP_BRAND_VOICE', 'Professional yet approachable, innovative, helpful, authentic')
        },
        
        'mcp': {
            'database': {
                'enabled': True,
                'type': 'sqlite',
                'connection_string': os.getenv('DATABASE_URL', 'sqlite:///./data/content.db')
            },
            'file_system': {
                'enabled': True,
                'root_path': './data'
            },
            'git': {
                'enabled': True,
                'repository_url': os.getenv('GIT_REPOSITORY_URL', 'https://github.com/yourusername/founder-socials-content'),
                'branch': 'main',
                'auto_commit': True
            },
            'web_search': {
                'enabled': True,
                'search_engine': 'google',
                'max_results': 5
            }
        },
        
        'content_strategy': {
            'blog_frequency': 2,
            'social_frequency': 5,
            'content_themes': ['innovation', 'growth', 'community', 'transparency'],
            'preferred_content_types': ['industry insights', 'startup lessons', 'product updates', 'team culture']
        },
        
        'publishing': {
            'auto_schedule': True,
            'buffer_time': 30,
            'timezone': 'UTC',
            'optimal_times': {
                'blog': ['10:00', '14:00'],
                'twitter': ['09:00', '12:00', '17:00'],
                'facebook': ['09:00', '15:00', '19:00'],
                'linkedin': ['08:00', '12:00', '17:00'],
                'instagram': ['12:00', '18:00', '20:00']
            }
        },
        
        'templates': {
            'blog_post': {
                'min_words': 800,
                'max_words': 2000,
                'structure': ['introduction', 'main_content', 'conclusion', 'call_to_action']
            },
            'social_post': {
                'include_hashtags': True,
                'include_cta': True,
                'max_length': {
                    'twitter': 280,
                    'facebook': 63206,
                    'linkedin': 1300,
                    'instagram': 2200
                }
            }
        },
        
        'logging': {
            'level': 'INFO',
            'file': './logs/founder_socials.log',
            'max_size': '10MB',
            'backup_count': 5
        }
    }
    
    return config

def save_config(config, config_path='config/config.yaml'):
    """Save configuration to YAML file"""
    config_dir = Path(config_path).parent
    config_dir.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)

if __name__ == "__main__":
    # Load configuration from environment variables
    config = load_config_from_env()
    
    # Save to config.yaml
    save_config(config)
    
    print("✅ Configuration loaded from environment variables and saved to config/config.yaml")
    print("🔧 Make sure to set all environment variables before running the application")
