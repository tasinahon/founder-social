"""
Content Generator for Founder Socials AI Agent

This module handles the generation of blog posts and social media content.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .ai_client import AIClient

logger = logging.getLogger(__name__)

class ContentGenerator:
    """
    Handles content generation for blogs and social media
    """
    
    def __init__(self, config: Dict):
        """Initialize the content generator"""
        self.config = config
        self.ai_client = AIClient(config.get('ai', {}))
        self.startup_info = config.get('startup', {})
        
        logger.info("Content Generator initialized")
    
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
            # Generate the blog post using AI
            content = await self.ai_client.generate_blog_post(
                topic=topic,
                startup_info=startup_info,
                template_config=template_config
            )
            
            # Add SEO optimization
            seo_content = await self._optimize_for_seo(content, topic)
            
            # Add call-to-action
            final_content = await self._add_call_to_action(seo_content, startup_info)
            
            logger.info(f"Blog post generated successfully: {len(final_content)} characters")
            return final_content
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            raise
    
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
            # Generate the social post using AI
            content = await self.ai_client.generate_social_post(
                topic=topic,
                platform=platform,
                startup_info=startup_info,
                template_config=template_config
            )
            
            # Optimize for platform
            optimized_content = await self._optimize_for_platform(content, platform)
            
            # Add engagement elements
            final_content = await self._add_engagement_elements(optimized_content, platform)
            
            logger.info(f"Social post generated successfully for {platform}: {len(final_content)} characters")
            return final_content
            
        except Exception as e:
            logger.error(f"Error generating social post: {e}")
            raise
    
    async def generate_content_variations(self, base_content: str, 
                                        content_type: str = 'social',
                                        num_variations: int = 3) -> List[str]:
        """
        Generate variations of existing content for A/B testing
        
        Args:
            base_content: The original content
            content_type: Type of content (blog or social)
            num_variations: Number of variations to generate
            
        Returns:
            List of content variations
        """
        logger.info(f"Generating {num_variations} variations for {content_type} content")
        
        try:
            variations = await self.ai_client.generate_content_variations(
                base_content=base_content,
                num_variations=num_variations
            )
            
            # Optimize each variation
            optimized_variations = []
            for variation in variations:
                if content_type == 'blog':
                    optimized = await self._optimize_for_seo(variation, "")
                else:
                    optimized = await self._optimize_for_platform(variation, "twitter")
                optimized_variations.append(optimized)
            
            logger.info(f"Generated {len(optimized_variations)} content variations")
            return optimized_variations
            
        except Exception as e:
            logger.error(f"Error generating content variations: {e}")
            return [base_content]
    
    async def _optimize_for_seo(self, content: str, topic: str) -> str:
        """
        Optimize blog content for SEO
        
        Args:
            content: The original content
            topic: The blog topic
            
        Returns:
            SEO-optimized content
        """
        try:
            # Create SEO optimization prompt
            prompt = f"""
            Optimize the following blog content for SEO:
            
            Topic: {topic}
            
            Content:
            {content}
            
            Please:
            1. Ensure proper heading structure (H1, H2, H3)
            2. Add relevant keywords naturally
            3. Include meta description
            4. Optimize for readability
            5. Add internal linking suggestions
            6. Ensure proper paragraph structure
            
            Return the optimized content with the same structure but improved for SEO.
            """
            
            optimized_content = await self.ai_client.generate_text(prompt, max_tokens=3000)
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error optimizing for SEO: {e}")
            return content
    
    async def _optimize_for_platform(self, content: str, platform: str) -> str:
        """
        Optimize content for specific social media platform
        
        Args:
            content: The original content
            platform: Target platform
            
        Returns:
            Platform-optimized content
        """
        try:
            platform_optimizations = {
                'twitter': {
                    'max_length': 280,
                    'hashtag_limit': 2,
                    'style': 'concise and engaging - SINGLE TWEET ONLY'
                },
                'linkedin': {
                    'max_length': 3000,
                    'hashtag_limit': 5,
                    'style': 'professional and informative'
                },
                'facebook': {
                    'max_length': 5000,
                    'hashtag_limit': 3,
                    'style': 'conversational and shareable'
                },
                'instagram': {
                    'max_length': 2200,
                    'hashtag_limit': 30,
                    'style': 'visual and engaging'
                }
            }
            
            config = platform_optimizations.get(platform, platform_optimizations['twitter'])
            
            # Special Twitter optimization prompt
            if platform.lower() == 'twitter':
                prompt = f"""
                Optimize this content for Twitter as a SINGLE TWEET ONLY:
                
                🚨 CRITICAL RULES:
                - MAXIMUM {config['max_length']} CHARACTERS TOTAL
                - EXACTLY ONE TWEET - NO THREADS, NO PARTS, NO CONTINUATIONS
                - NO mentions of "thread", "1/n", "[2/6]", "see thread", or similar
                - Complete the entire message in ONE tweet
                
                Original content:
                {content}
                
                MANDATORY OPTIMIZATION:
                1. Condense into ONE tweet under {config['max_length']} characters
                2. Count every character (letters, spaces, emojis, hashtags, punctuation)
                3. Keep the core message and value
                4. Include 1-2 relevant hashtags
                5. Make it engaging and complete
                6. Add emoji if space allows
                
                The result MUST be a complete, standalone tweet under {config['max_length']} characters.
                
                Return ONLY the optimized tweet content - no explanations.
                """
            else:
                prompt = f"""
                Optimize the following content for {platform.upper()}:
                
                🚨 CRITICAL CHARACTER LIMIT: {config['max_length']} CHARACTERS (NOT WORDS)
                
                Count EVERY character including letters, spaces, punctuation, emojis, hashtags.
                
                Platform requirements:
                - Style: {config['style']}
                - Hashtag limit: {config['hashtag_limit']}
                
                Original content:
                {content}
                
                MANDATORY TASKS:
                1. Rewrite to fit EXACTLY under {config['max_length']} characters
                2. Count every single character to verify
                3. If over limit, cut content until under {config['max_length']} characters
                4. Maintain the core message
                5. Keep it engaging
                
                The final result MUST be under {config['max_length']} characters total.
                
                Please optimize the content to:
                1. STRICTLY fit within {config['max_length']} CHARACTER limit (count each letter/space/symbol)
                2. Match platform style and tone
                3. Include appropriate hashtags
                4. Maximize engagement potential
                5. Follow platform best practices
                
                Return the optimized content.
                """
            
            optimized_content = await self.ai_client.generate_text(prompt, max_tokens=1000)
            
            # Validate character limit and force truncation if needed
            max_length = config['max_length']
            if len(optimized_content) > max_length:
                logger.warning(f"AI optimization failed - content still {len(optimized_content)} chars, truncating to {max_length}")
                # Smart truncation - try to end at a sentence or word boundary
                if max_length > 20:  # Only if we have reasonable space
                    truncated = optimized_content[:max_length-3]
                    # Try to end at sentence boundary
                    last_sentence = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                    if last_sentence > max_length * 0.7:  # If sentence boundary is not too far back
                        optimized_content = truncated[:last_sentence+1]
                    else:
                        # Try to end at word boundary
                        last_space = truncated.rfind(' ')
                        if last_space > max_length * 0.8:  # If word boundary is reasonable
                            optimized_content = truncated[:last_space] + "..."
                        else:
                            optimized_content = truncated + "..."
                else:
                    optimized_content = optimized_content[:max_length]
                    
                logger.info(f"Content truncated to {len(optimized_content)} characters")
            else:
                logger.info(f"✅ Content fits within {platform} limit: {len(optimized_content)}/{max_length} chars")
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error optimizing for platform: {e}")
            return content
    
    async def _add_call_to_action(self, content: str, startup_info: Dict) -> str:
        """
        Add appropriate call-to-action to blog content
        
        Args:
            content: The blog content
            startup_info: Startup information
            
        Returns:
            Content with call-to-action
        """
        try:
            # Create CTA prompt
            prompt = f"""
            Add a compelling call-to-action to the following blog content:
            
            Startup: {startup_info.get('name', 'Unknown')}
            Industry: {startup_info.get('industry', 'Technology')}
            
            Content:
            {content}
            
            Please add a call-to-action that:
            1. Is relevant to the content
            2. Encourages engagement
            3. Aligns with startup goals
            4. Is not overly promotional
            5. Provides value to readers
            
            Return the content with the call-to-action added at the end.
            """
            
            content_with_cta = await self.ai_client.generate_text(prompt, max_tokens=2000)
            return content_with_cta
            
        except Exception as e:
            logger.error(f"Error adding call-to-action: {e}")
            return content
    
    async def _add_engagement_elements(self, content: str, platform: str) -> str:
        """
        Add engagement elements to social media content
        
        Args:
            content: The social media content
            platform: Target platform
            
        Returns:
            Content with engagement elements
        """
        try:
            # Special handling for Twitter - NO THREADS, single tweet only
            if platform.lower() == 'twitter':
                prompt = f"""
                Add engagement elements to this SINGLE Twitter post (NO THREADS):
                
                Content:
                {content}
                
                🚨 CRITICAL RULES:
                - KEEP AS ONE TWEET ONLY (under 280 characters total)
                - NO thread creation, NO "1/n", NO "see thread", NO continuations
                - Add ONLY simple engagement like questions or polls
                - Count characters to ensure under 280 total
                
                Available engagement options:
                - Add a simple question at the end
                - Add a poll suggestion (but count characters)
                - Add a call for comments/replies
                
                MANDATORY: Final result must be ONE complete tweet under 280 characters.
                
                Return the single tweet with engagement elements.
                """
            else:
                engagement_elements = {
                    'linkedin': ['question', 'insight', 'story'],
                    'facebook': ['question', 'poll', 'story'],
                    'instagram': ['question', 'story', 'visual']
                }
                
                elements = engagement_elements.get(platform, ['question'])
                
                prompt = f"""
                Add engagement elements to the following {platform} post:
                
                Content:
                {content}
                
                Available engagement elements: {', '.join(elements)}
                
                Please add one or more engagement elements that:
                1. Encourage comments and interaction
                2. Are relevant to the content
                3. Match platform best practices
                4. Increase shareability
                
                Return the content with engagement elements added.
                """
            
            content_with_engagement = await self.ai_client.generate_text(prompt, max_tokens=1000)
            return content_with_engagement
            
        except Exception as e:
            logger.error(f"Error adding engagement elements: {e}")
            return content
    
    async def generate_thread_content(self, main_topic: str, num_tweets: int = 5) -> List[str]:
        """
        Generate a Twitter thread
        
        Args:
            main_topic: The main topic for the thread
            num_tweets: Number of tweets in the thread
            
        Returns:
            List of tweets for the thread
        """
        logger.info(f"Generating Twitter thread with {num_tweets} tweets for topic: {main_topic}")
        
        try:
            prompt = f"""
            Create a Twitter thread about: "{main_topic}"
            
            Requirements:
            - Number of tweets: {num_tweets}
            - Each tweet should be under 280 characters
            - Thread should tell a complete story or provide comprehensive information
            - Include relevant hashtags
            - Make it engaging and shareable
            - Each tweet should flow naturally to the next
            
            Startup context:
            - Name: {self.startup_info.get('name', 'Unknown')}
            - Industry: {self.startup_info.get('industry', 'Technology')}
            - Brand voice: {self.startup_info.get('brand_voice', 'Professional and innovative')}
            
            Format each tweet as "Tweet 1:", "Tweet 2:", etc.
            """
            
            response = await self.ai_client.generate_text(prompt, max_tokens=2000)
            
            # Parse the thread
            thread_tweets = self._parse_thread_tweets(response, num_tweets)
            
            logger.info(f"Generated Twitter thread with {len(thread_tweets)} tweets")
            return thread_tweets
            
        except Exception as e:
            logger.error(f"Error generating Twitter thread: {e}")
            return [f"Error generating thread about {main_topic}"]
    
    def _parse_thread_tweets(self, response: str, num_tweets: int) -> List[str]:
        """Parse AI response to extract thread tweets"""
        tweets = []
        
        try:
            lines = response.split('\n')
            current_tweet = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('Tweet') and ':' in line:
                    if current_tweet:
                        tweets.append(current_tweet.strip())
                    current_tweet = line.split(':', 1)[1].strip()
                elif line and current_tweet:
                    current_tweet += " " + line
            
            if current_tweet:
                tweets.append(current_tweet.strip())
            
            # Ensure we have the right number of tweets
            while len(tweets) < num_tweets:
                tweets.append(f"Additional tweet {len(tweets) + 1} for the thread")
            
            return tweets[:num_tweets]
            
        except Exception as e:
            logger.error(f"Error parsing thread tweets: {e}")
            return [f"Tweet {i+1}" for i in range(num_tweets)]
    
    async def generate_linkedin_article(self, topic: str) -> str:
        """
        Generate a LinkedIn article
        
        Args:
            topic: The article topic
            
        Returns:
            Generated LinkedIn article
        """
        logger.info(f"Generating LinkedIn article for topic: {topic}")
        
        try:
            prompt = f"""
            Write a LinkedIn article about: "{topic}"
            
            Requirements:
            - Professional tone
            - 800-1500 words
            - Include relevant insights and data
            - Add value to the professional community
            - Include a compelling headline
            - Use proper formatting with headings
            - Include relevant hashtags
            - End with a call-to-action
            
            Startup context:
            - Name: {self.startup_info.get('name', 'Unknown')}
            - Industry: {self.startup_info.get('industry', 'Technology')}
            - Brand voice: {self.startup_info.get('brand_voice', 'Professional and innovative')}
            
            Write the article in markdown format.
            """
            
            article = await self.ai_client.generate_text(prompt, max_tokens=3000)
            
            logger.info(f"LinkedIn article generated successfully: {len(article)} characters")
            return article
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn article: {e}")
            raise 