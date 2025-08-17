#!/usr/bin/env python3
"""
Test script for GPT-4o integration
"""

import asyncio
import logging
from agent.ai_client import AIClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_gpt4o_simple():
    """Simple test for GPT-4o"""
    logger.info("Testing GPT-4o with simple prompt...")
    
    # Configure GPT-4o
    config = {
        'provider': 'gpt4o',
        'gpt4o': {
            'api_key': 'your_gpt4o_api_key_here',
            'endpoint': 'https://your-resource.openai.azure.com/openai/deployments/gpt-4o',
            'temperature': 0.7
        }
    }
    
    try:
        ai_client = AIClient(config)
        logger.info("GPT-4o client initialized successfully")
        
        # Test with a simple prompt
        prompt = "Hello, how are you today?"
        response = await ai_client.generate_text(prompt, max_tokens=50)
        
        if response:
            logger.info(f"✅ GPT-4o response: {response}")
            return True
        else:
            logger.error("❌ Empty response from GPT-4o")
            return False
            
    except Exception as e:
        logger.error(f"❌ GPT-4o test failed: {e}")
        return False

async def test_gpt4o_blog_generation():
    """Test blog post generation with GPT-4o"""
    logger.info("Testing blog post generation with GPT-4o...")
    
    config = {
        'provider': 'gpt4o',
        'gpt4o': {
            'api_key': 'your_gpt4o_api_key_here',
            'endpoint': 'https://your-resource.openai.azure.com/openai/deployments/gpt-4o',
            'temperature': 0.7
        }
    }
    
    startup_info = {
        'name': 'Test Startup',
        'industry': 'Technology',
        'description': 'A technology startup focused on AI solutions',
        'target_audience': 'Startup founders and tech professionals',
        'brand_voice': 'Professional and innovative'
    }
    
    template_config = {
        'structure': ['Introduction', 'Main Content', 'Conclusion'],
        'min_words': 200,
        'max_words': 500
    }
    
    try:
        ai_client = AIClient(config)
        
        blog_post = await ai_client.generate_blog_post(
            "AI in Startups",
            startup_info,
            template_config
        )
        
        if blog_post and len(blog_post) > 100:
            logger.info(f"✅ Blog post generated successfully: {len(blog_post)} characters")
            logger.info(f"Preview: {blog_post[:200]}...")
            return True
        else:
            logger.error("❌ Blog post generation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Blog generation test failed: {e}")
        return False

async def test_gpt4o_social_post():
    """Test social media post generation with GPT-4o"""
    logger.info("Testing social media post generation with GPT-4o...")
    
    config = {
        'provider': 'gpt4o',
        'gpt4o': {
            'api_key': 'your_gpt4o_api_key_here',
            'endpoint': 'https://your-resource.openai.azure.com/openai/deployments/gpt-4o',
            'temperature': 0.7
        }
    }
    
    startup_info = {
        'name': 'Test Startup',
        'industry': 'Technology',
        'description': 'A technology startup focused on AI solutions',
        'target_audience': 'Startup founders and tech professionals',
        'brand_voice': 'Professional and innovative'
    }
    
    template_config = {
        'linkedin': {
            'max_length': 300,
            'include_hashtags': True
        }
    }
    
    try:
        ai_client = AIClient(config)
        
        social_post = await ai_client.generate_social_post(
            "AI in Startups",
            "linkedin",
            startup_info,
            template_config
        )
        
        if social_post and len(social_post) > 10:
            logger.info(f"✅ Social post generated successfully: {len(social_post)} characters")
            logger.info(f"Content: {social_post}")
            return True
        else:
            logger.error("❌ Social post generation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Social post generation test failed: {e}")
        return False

async def main():
    """Run tests"""
    logger.info("🎯 Starting GPT-4o Integration Tests")
    logger.info("=" * 50)
    
    # Test simple text generation
    simple_success = await test_gpt4o_simple()
    
    logger.info("\n" + "=" * 50)
    
    # Test blog generation
    blog_success = await test_gpt4o_blog_generation()
    
    logger.info("\n" + "=" * 50)
    
    # Test social post generation
    social_success = await test_gpt4o_social_post()
    
    logger.info("\n" + "=" * 50)
    logger.info("📊 Test Results:")
    logger.info(f"Simple Text Generation: {'✅ PASS' if simple_success else '❌ FAIL'}")
    logger.info(f"Blog Post Generation: {'✅ PASS' if blog_success else '❌ FAIL'}")
    logger.info(f"Social Post Generation: {'✅ PASS' if social_success else '❌ FAIL'}")
    
    if simple_success or blog_success or social_success:
        logger.info("\n🎉 GPT-4o integration is working!")
        logger.info("The AI agent can now use GPT-4o for content generation.")
    else:
        logger.error("\n❌ GPT-4o integration needs attention.")

if __name__ == "__main__":
    asyncio.run(main()) 