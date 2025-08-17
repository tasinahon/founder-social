"""
AI Client for Founder Socials AI Agent

This module handles communication with different AI providers for content generation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import openai
from openai import AsyncOpenAI, AzureOpenAI

# Try to import Azure AI Inference, but don't fail if not available
try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_AI_AVAILABLE = True
except ImportError:
    print("⚠️  Azure AI Inference not available - Azure AI features will be disabled")
    ChatCompletionsClient = None
    AzureKeyCredential = None
    AZURE_AI_AVAILABLE = False

from datetime import datetime

logger = logging.getLogger(__name__)

class AIClient:
    """
    Client for interacting with AI providers
    """
    
    def __init__(self, config: Dict):
        """Initialize the AI client with configuration"""
        self.config = config
        self.provider = config.get('provider', 'openai')
        self.model = config.get('model', 'gpt-4-turbo-preview')
        self.temperature = config.get('temperature', 0.7)
        
        # Initialize provider-specific clients
        if self.provider == 'openai':
            self._init_openai_client(config)
        elif self.provider == 'azure_openai':
            self._init_azure_openai_client(config)
        elif self.provider == 'deepseek_r1':
            self._init_deepseek_r1_client(config)
        elif self.provider == 'gpt4o':
            self._init_gpt4o_client(config)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
        
        logger.info(f"AI Client initialized with provider: {self.provider}")
    
    def _init_openai_client(self, config: Dict):
        """Initialize OpenAI client"""
        api_key = config.get('openai', {}).get('api_key')
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = config.get('openai', {}).get('model', 'gpt-4-turbo-preview')
        self.temperature = config.get('openai', {}).get('temperature', 0.7)
    
    def _init_azure_openai_client(self, config: Dict):
        """Initialize Azure OpenAI client"""
        azure_config = config.get('azure_openai', {})
        api_key = azure_config.get('api_key')
        azure_endpoint = azure_config.get('azure_endpoint')
        api_version = azure_config.get('api_version', '2024-12-01-preview')
        
        if not api_key or not azure_endpoint:
            raise ValueError("Azure OpenAI API key or endpoint not provided")
        
        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key
        )
        self.model = azure_config.get('model', 'gpt-4-turbo-preview')
        self.temperature = azure_config.get('temperature', 0.7)
    
    def _init_deepseek_r1_client(self, config: Dict):
        """Initialize DeepSeek-R1 client using Azure OpenAI"""
        deepseek_config = config.get('deepseek_r1', {})
        api_key = deepseek_config.get('api_key')
        azure_endpoint = deepseek_config.get('azure_endpoint')
        api_version = deepseek_config.get('api_version', '2024-12-01-preview')
        model_name = deepseek_config.get('model', 'gpt-4')  # Default to gpt-4 if no model specified
        
        if not api_key or not azure_endpoint:
            raise ValueError("DeepSeek-R1 API key or endpoint not provided")
        
        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key
        )
        self.model = model_name  # Use configured model name instead of hardcoded
        self.temperature = deepseek_config.get('temperature', 0.7)
        
        logger.info(f"Initialized DeepSeek-R1 client with model: {self.model}")
    
    def _init_gpt4o_client(self, config: Dict):
        """Initialize GPT-4o client using Azure AI Inference"""
        if not AZURE_AI_AVAILABLE:
            raise ValueError("Azure AI Inference not available - cannot use GPT-4o provider")
            
        gpt4o_config = config.get('gpt4o', {})
        api_key = gpt4o_config.get('api_key')
        endpoint = gpt4o_config.get('endpoint')
        
        if not api_key or not endpoint:
            raise ValueError("GPT-4o API key or endpoint not provided")
        
        self.client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
        )
        self.model = "gpt-4o"  # Fixed model name for GPT-4o
        self.temperature = gpt4o_config.get('temperature', 0.7)
    
    async def generate_text(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Generate text using the configured AI provider
        
        Args:
            prompt: The prompt to send to the AI
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            if self.provider == 'openai':
                return await self._generate_openai_text(prompt, max_tokens)
            elif self.provider == 'azure_openai':
                return await self._generate_azure_openai_text(prompt, max_tokens)
            elif self.provider == 'deepseek_r1':
                return await self._generate_deepseek_r1_text(prompt, max_tokens)
            elif self.provider == 'gpt4o':
                return await self._generate_gpt4o_text(prompt, max_tokens)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def _generate_openai_text(self, prompt: str, max_tokens: int) -> str:
        """Generate text using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional content creator and strategist for startups. Always write in plain text without markdown formatting like **bold** or *italic*. Use natural language emphasis only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_azure_openai_text(self, prompt: str, max_tokens: int) -> str:
        """Generate text using Azure OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional content creator and strategist for startups. Always write in plain text without markdown formatting like **bold** or *italic*. Use natural language emphasis only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    return content
                else:
                    raise ValueError("Empty response content from Azure OpenAI")
            else:
                raise ValueError("Invalid response structure from Azure OpenAI")
            
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            raise
    
    async def _generate_deepseek_r1_text(self, prompt: str, max_tokens: int) -> str:
        """Generate text using DeepSeek-R1 via Azure OpenAI"""
        try:
            logger.info(f"Generating content with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional content creator and strategist for startups. Always write in plain text without markdown formatting like **bold** or *italic*. Use natural language emphasis only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content and content.strip():
                    logger.info(f"Successfully generated {len(content)} characters of content")
                    return content.strip()
                else:
                    logger.error("Empty response content from API")
                    raise ValueError("Empty response content from DeepSeek-R1")
            else:
                logger.error("Invalid response structure from API")
                raise ValueError("Invalid response structure from DeepSeek-R1")
            
        except Exception as e:
            logger.error(f"DeepSeek-R1 API error: {e}")
            # Log more details about the error
            if hasattr(e, 'response'):
                logger.error(f"API response: {e.response}")
            raise
    
    async def _generate_gpt4o_text(self, prompt: str, max_tokens: int) -> str:
        """Generate text using GPT-4o via Azure AI Inference"""
        try:
            response = self.client.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional content creator and strategist for startups. Always write in plain text without markdown formatting like **bold** or *italic*. Use natural language emphasis only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    return content
                else:
                    raise ValueError("Empty response content from GPT-4o")
            else:
                raise ValueError("Invalid response structure from GPT-4o")
            
        except Exception as e:
            logger.error(f"GPT-4o API error: {e}")
            raise
    
    async def generate_blog_post(self, topic: str, startup_info: Dict, 
                               template_config: Dict) -> str:
        """
        Generate a complete blog post
        
        Args:
            topic: The blog post topic
            startup_info: Information about the startup
            template_config: Blog post template configuration
            
        Returns:
            Generated blog post content
        """
        logger.info(f"Generating blog post for topic: {topic}")
        
        try:
            # Create blog post prompt
            prompt = self._create_blog_post_prompt(topic, startup_info, template_config)
            
            # Generate content
            content = await self.generate_text(prompt, max_tokens=3000)
            
            # Format the content
            formatted_content = self._format_blog_post(content, topic, startup_info)
            
            logger.info(f"Blog post generated successfully")
            return formatted_content
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            raise
    
    def _create_blog_post_prompt(self, topic: str, startup_info: Dict, 
                                template_config: Dict) -> str:
        """Create a prompt for blog post generation"""
        structure = template_config.get('structure', [
            'Introduction', 'Problem Statement', 'Solution', 
            'Implementation', 'Results', 'Conclusion'
        ])
        
        min_words = template_config.get('min_words', 800)
        max_words = template_config.get('max_words', 2000)
        
        return f"""
        Write a comprehensive blog post about: "{topic}"
        
        Startup Information:
        - Name: {startup_info.get('name', 'Unknown')}
        - Industry: {startup_info.get('industry', 'Technology')}
        - Description: {startup_info.get('description', 'A technology startup')}
        - Target Audience: {startup_info.get('target_audience', 'Startup founders')}
        - Brand Voice: {startup_info.get('brand_voice', 'Professional and innovative')}
        
        Requirements:
        - Word count: {min_words}-{max_words} words
        - Structure: {', '.join(structure)}
        - Tone: {startup_info.get('brand_voice', 'Professional and engaging')}
        - Include relevant examples and insights
        - Make it educational and valuable for the target audience
        - Include a compelling introduction and conclusion
        - Use clear headings and subheadings
        - Include actionable takeaways
        
        Write the blog post in clean, readable format with clear headings and structure.
        Do not use markdown formatting like **bold** or *italic* - use natural emphasis only.
        """
    
    def _format_blog_post(self, content: str, topic: str, startup_info: Dict) -> str:
        """Format the generated blog post"""
        # Add frontmatter
        frontmatter = f"""---
title: "{topic}"
author: "{startup_info.get('name', 'Startup Team')}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
description: "A comprehensive guide on {topic.lower()}"
tags: ["startup", "business", "{startup_info.get('industry', 'technology').lower()}"]
---

"""
        
        return frontmatter + content
    
    async def generate_social_post(self, topic: str, platform: str, 
                                 startup_info: Dict, template_config: Dict) -> str:
        """
        Generate a social media post
        
        Args:
            topic: The post topic
            platform: Target platform (twitter, linkedin, facebook, instagram)
            startup_info: Information about the startup
            template_config: Social post template configuration
            
        Returns:
            Generated social media post
        """
        logger.info(f"Generating social post for {platform}: {topic}")
        
        try:
            # Get platform-specific configuration
            platform_config = template_config.get(platform, {})
            max_length = platform_config.get('max_length', 280)
            include_hashtags = platform_config.get('include_hashtags', True)
            
            # Create social post prompt
            prompt = self._create_social_post_prompt(topic, platform, startup_info, max_length)
            
            # Generate content
            content = await self.generate_text(prompt, max_tokens=500)
            
            # Format and optimize for platform
            formatted_content = self._format_social_post(content, platform, startup_info, include_hashtags)
            
            logger.info(f"Social post generated successfully for {platform}")
            return formatted_content
            
        except Exception as e:
            logger.error(f"Error generating social post: {e}")
            raise
    
    def _create_social_post_prompt(self, topic: str, platform: str, 
                                 startup_info: Dict, max_length: int) -> str:
        """Create a prompt for social media post generation"""
        
        # Special Twitter handling for single tweet only
        if platform.lower() == 'twitter':
            return f"""
            Write a SINGLE Twitter post (tweet) about: "{topic}"
            
            🚨 ABSOLUTE REQUIREMENTS:
            - EXACTLY ONE TWEET ONLY - NO THREADS, NO MULTIPLE PARTS
            - MAXIMUM {max_length} CHARACTERS TOTAL (count each letter, space, emoji, punctuation)
            - NO mentions of "thread", "1/n", "[2/6]", or continuation indicators
            - Complete message in ONE tweet only
            
            Startup Information:
            - Name: {startup_info.get('name', 'Unknown')}
            - Industry: {startup_info.get('industry', 'Technology')}
            - Brand Voice: {startup_info.get('brand_voice', 'Professional and innovative')}
            
            Content Requirements:
            - Concise and engaging
            - Include 1-2 relevant hashtags
            - Add a call-to-action if space allows
            - Use emojis strategically
            - Professional yet conversational tone
            
            ⚠️ CHARACTER COUNTING RULES:
            - Count every letter, number, space, punctuation mark
            - Emojis count as 1-2 characters each
            - Hashtags count fully (#StartupTips = 12 characters)
            - The final tweet MUST be under {max_length} characters
            
            Write ONLY the tweet content - no explanations, no formatting, just the plain text tweet.
            """
        
        # Guidelines for other platforms
        platform_guidelines = {
            'linkedin': 'Professional tone, focus on business value and insights. Include relevant hashtags.',
            'facebook': 'Conversational tone, engaging and shareable content. Include relevant hashtags.',
            'instagram': 'Visual and engaging content. Include relevant hashtags and emojis.'
        }
        
        return f"""
        Write a social media post about: "{topic}"
        
        Platform: {platform.upper()}
        
        ⚠️  CRITICAL CHARACTER LIMIT: {max_length} CHARACTERS (NOT WORDS - COUNT EACH LETTER, SPACE, EMOJI, ETC.)
        
        Platform guidelines: {platform_guidelines.get(platform, 'Engaging and relevant content')}
        
        Startup Information:
        - Name: {startup_info.get('name', 'Unknown')}
        - Industry: {startup_info.get('industry', 'Technology')}
        - Brand Voice: {startup_info.get('brand_voice', 'Professional and innovative')}
        
        🚨 MANDATORY: The complete post must be EXACTLY UNDER {max_length} CHARACTERS.
        
        Count every single character including:
        - Letters and numbers
        - Spaces and punctuation
        - Emojis (count as 1-2 characters each)
        - Hashtags and symbols
        
        Requirements:
        - TOTAL CHARACTER COUNT MUST BE < {max_length}
        - Engaging and shareable content  
        - Appropriate for {platform} audience
        - Include 1-2 relevant hashtags
        - Write the complete post, then count characters to verify it's under {max_length}
        - Add value to the audience
        - Include a call-to-action when appropriate
        - Stay within character limit
        
        Write the post content only, without any additional formatting or markdown.
        Do not use **bold**, *italic*, or any other markdown formatting.
        Use plain text with emojis and natural emphasis only.
        """
    
    def _format_social_post(self, content: str, platform: str, 
                          startup_info: Dict, include_hashtags: bool) -> str:
        """Format the generated social media post"""
        # Clean up the content
        content = content.strip()
        
        # Add hashtags if requested
        if include_hashtags:
            hashtags = self._get_relevant_hashtags(platform, startup_info)
            if hashtags:
                content += f"\n\n{' '.join(hashtags)}"
        
        return content
    
    def _get_relevant_hashtags(self, platform: str, startup_info: Dict) -> List[str]:
        """Get relevant hashtags for the platform and startup"""
        base_hashtags = ['#startup', '#entrepreneurship']
        
        # Add industry-specific hashtags
        industry = startup_info.get('industry', 'Technology').lower()
        if 'tech' in industry or 'technology' in industry:
            base_hashtags.append('#tech')
        elif 'fintech' in industry:
            base_hashtags.append('#fintech')
        elif 'health' in industry:
            base_hashtags.append('#healthtech')
        
        # Add platform-specific hashtags
        if platform == 'linkedin':
            base_hashtags.extend(['#business', '#innovation'])
        elif platform == 'twitter':
            base_hashtags.extend(['#startup', '#tech'])
        elif platform == 'instagram':
            base_hashtags.extend(['#startup', '#entrepreneur'])
        
        return base_hashtags[:5]  # Limit to 5 hashtags
    
    async def generate_content_variations(self, base_content: str, 
                                        num_variations: int = 3) -> List[str]:
        """
        Generate variations of existing content
        
        Args:
            base_content: The original content
            num_variations: Number of variations to generate
            
        Returns:
            List of content variations
        """
        logger.info(f"Generating {num_variations} content variations")
        
        try:
            prompt = f"""
            Create {num_variations} different variations of the following content. 
            Each variation should maintain the same core message but use different:
            - Writing style
            - Tone
            - Structure
            - Examples or analogies
            
            Original content:
            {base_content}
            
            Provide each variation as a separate, clearly marked section.
            """
            
            response = await self.generate_text(prompt, max_tokens=2000)
            
            # Parse variations
            variations = self._parse_content_variations(response, num_variations)
            
            logger.info(f"Generated {len(variations)} content variations")
            return variations
            
        except Exception as e:
            logger.error(f"Error generating content variations: {e}")
            return [base_content]  # Return original if generation fails
    
    def _parse_content_variations(self, response: str, num_variations: int) -> List[str]:
        """Parse AI response to extract content variations"""
        variations = []
        
        try:
            # Simple parsing - split by common variation markers
            parts = response.split('Variation')
            for part in parts[1:]:  # Skip the first part (before "Variation")
                if part.strip():
                    variations.append(part.strip())
            
            # If parsing didn't work, split by other common markers
            if len(variations) < num_variations:
                parts = response.split('---')
                for part in parts:
                    if part.strip() and len(variations) < num_variations:
                        variations.append(part.strip())
            
            # Ensure we have the requested number of variations
            while len(variations) < num_variations:
                variations.append(variations[0] if variations else "No variation available")
            
            return variations[:num_variations]
            
        except Exception as e:
            logger.error(f"Error parsing content variations: {e}")
            return [response]  # Return original response if parsing fails 