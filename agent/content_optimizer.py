"""
Content Optimizer for Founder Socials AI Agent

This module handles content optimization, SEO, readability, and strategy optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import re
from datetime import datetime, timedelta

from .ai_client import AIClient

logger = logging.getLogger(__name__)

class ContentOptimizer:
    """
    Handles content optimization and strategy recommendations
    """
    
    def __init__(self, config: Dict):
        """Initialize the content optimizer"""
        self.config = config
        self.ai_client = AIClient(config.get('ai', {}))
        
        logger.info("Content Optimizer initialized")
    
    async def optimize_content(self, content: str, platform: str, 
                             content_type: str) -> str:
        """
        Optimize content for the specified platform and type
        
        Args:
            content: The content to optimize
            platform: Target platform
            content_type: Type of content (blog or social)
            
        Returns:
            Optimized content
        """
        logger.info(f"Optimizing {content_type} content for {platform}")
        
        try:
            # Apply platform-specific optimizations
            optimized_content = await self._apply_platform_optimizations(
                content, platform, content_type
            )
            
            # Enforce platform-specific character limits after platform optimization
            optimized_content = self._enforce_platform_limits(optimized_content, platform)
            
            # Optimize for engagement
            optimized_content = await self._optimize_for_engagement(
                optimized_content, platform
            )
            
            # Enforce platform-specific character limits after engagement optimization
            optimized_content = self._enforce_platform_limits(optimized_content, platform)
            
            # Check readability
            readability_score = await self._check_readability(optimized_content)
            
            # Apply final optimizations based on readability
            if readability_score < 0.7:
                optimized_content = await self._improve_readability(optimized_content)
                
                # Enforce platform-specific character limits after readability improvement
                optimized_content = self._enforce_platform_limits(optimized_content, platform)

            logger.info(f"Content optimization completed for {platform}")
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            return content
    
    async def _apply_platform_optimizations(self, content: str, platform: str, 
                                          content_type: str) -> str:
        """Apply platform-specific optimizations"""
        try:
            platform_configs = {
                'twitter': {
                    'max_length': 280,
                    'hashtag_limit': 2,
                    'style': 'concise and engaging',
                    'features': ['single_tweet', 'polls', 'questions']
                },
                'linkedin': {
                    'max_length': 3000,
                    'hashtag_limit': 5,
                    'style': 'professional and informative',
                    'features': ['articles', 'insights', 'stories']
                },
                'facebook': {
                    'max_length': 5000,
                    'hashtag_limit': 3,
                    'style': 'conversational and shareable',
                    'features': ['stories', 'polls', 'questions']
                },
                'instagram': {
                    'max_length': 2200,
                    'hashtag_limit': 30,
                    'style': 'visual and engaging',
                    'features': ['stories', 'reels', 'carousels']
                },
                'wordpress': {
                    'max_length': None,
                    'hashtag_limit': None,
                    'style': 'comprehensive and SEO-optimized',
                    'features': ['SEO', 'internal_links', 'meta_tags']
                }
            }
            
            config = platform_configs.get(platform, platform_configs['twitter'])
            
            # Platform-specific optimization prompts
            if platform.lower() == 'twitter':
                prompt = f"""
                Optimize the following content for TWITTER:
                
                Platform requirements:
                - Style: {config['style']}
                - Max length: {config['max_length']} characters
                - Content type: {content_type}
                - Features: {', '.join(config['features'])}
                
                Original content:
                {content}
                
                ⚠️ TWITTER REQUIREMENTS:
                - Create ONLY a single tweet, NOT a thread
                - Do not add "Tweet 1:", "1/", "[1/]", or thread indicators
                - Keep under {config['max_length']} characters
                - Make it one complete tweet
                
                Return ONLY the Twitter-optimized single tweet.
                """
            
            else:
                prompt = f"""
                Optimize the following content for {platform.upper()}:
                
                Platform requirements:
                - Style: {config['style']}
                - Max length: {config['max_length'] or 'No limit'}
                - Hashtag limit: {config['hashtag_limit'] or 'No limit'}
                - Content type: {content_type}
                - Features: {', '.join(config['features'])}
                
                Original content:
                {content}
                
                Please optimize the content to:
                1. Match {platform} style and tone
                2. Follow {platform} best practices
                3. Maximize engagement for {platform} audience
                4. Include appropriate {platform} features
                5. Stay within {platform} character limits if applicable
                
                Return ONLY the {platform}-optimized content.
                """
            
            optimized_content = await self.ai_client.generate_text(prompt, max_tokens=2000)
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error applying platform optimizations: {e}")
            return content
    
    async def _optimize_for_engagement(self, content: str, platform: str) -> str:
        """Optimize content for maximum engagement"""
        try:
            engagement_strategies = {
                'twitter': ['questions', 'polls', 'single_tweet', 'hashtags'],
                'linkedin': ['insights', 'stories', 'questions', 'professional_tips'],
                'facebook': ['stories', 'polls', 'questions', 'shareable_content'],
                'instagram': ['visual_content', 'stories', 'questions', 'trending_hashtags']
            }
            
            strategies = engagement_strategies.get(platform, ['questions'])
            
            # Platform-specific prompts
            if platform.lower() == 'twitter':
                prompt = f"""
                Optimize the following content for maximum engagement on TWITTER:
                
                Content:
                {content}
                
                Engagement strategies: {', '.join(strategies)}
                
                ⚠️ TWITTER REQUIREMENTS:
                - Keep as SINGLE tweet under 280 characters
                - NO threads, numbered lists, or multiple parts
                - Add simple engagement (questions, polls only)
                - Count characters to stay under 280
                
                Enhance to encourage comments and interactions as ONE complete tweet.
                Return ONLY the Twitter-optimized content.
                """
            
            elif platform.lower() == 'facebook':
                prompt = f"""
                Optimize the following content for maximum engagement on FACEBOOK:
                
                Content:
                {content}
                
                Engagement strategies: {', '.join(strategies)}
                
                🎯 FACEBOOK REQUIREMENTS:
                - Create engaging, shareable content
                - Use Facebook's longer format (up to 63,000 characters)
                - Add polls, questions, calls-to-action
                - Encourage comments and sharing
                - Use emojis and casual tone
                
                Enhance to maximize Facebook engagement and shareability.
                Return ONLY the Facebook-optimized content.
                """
            
            elif platform.lower() == 'linkedin':
                prompt = f"""
                Optimize the following content for maximum engagement on LINKEDIN:
                
                Content:
                {content}
                
                Engagement strategies: {', '.join(strategies)}
                
                💼 LINKEDIN REQUIREMENTS:
                - Professional, business-focused tone
                - Share insights and valuable lessons
                - Use LinkedIn's format (up to 3,000 characters)
                - Add thought-provoking questions
                - Include professional hashtags
                
                Enhance to maximize LinkedIn professional engagement.
                Return ONLY the LinkedIn-optimized content.
                """
            
            else:
                # Generic prompt for other platforms
                prompt = f"""
                Optimize the following content for maximum engagement on {platform}:
                
                Content:
                {content}
                
                Engagement strategies: {', '.join(strategies)}
                
                Please enhance the content to:
                1. Encourage comments and interactions
                2. Increase shareability
                3. Spark conversations
                4. Add relevant engagement elements
                5. Make it more compelling
                
                Return the engagement-optimized content.
                """
            
            optimized_content = await self.ai_client.generate_text(prompt, max_tokens=1500)
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error optimizing for engagement: {e}")
            return content
    
    async def _check_readability(self, content: str) -> float:
        """Check content readability score"""
        try:
            # Simple readability metrics
            words = content.split()
            sentences = re.split(r'[.!?]+', content)
            paragraphs = content.split('\n\n')
            
            # Calculate basic metrics
            avg_words_per_sentence = len(words) / max(len(sentences), 1)
            avg_sentences_per_paragraph = len(sentences) / max(len(paragraphs), 1)
            
            # Simple readability score (0-1)
            readability_score = 1.0
            
            # Penalize very long sentences
            if avg_words_per_sentence > 25:
                readability_score -= 0.2
            elif avg_words_per_sentence > 20:
                readability_score -= 0.1
            
            # Penalize very long paragraphs
            if avg_sentences_per_paragraph > 8:
                readability_score -= 0.2
            elif avg_sentences_per_paragraph > 5:
                readability_score -= 0.1
            
            # Bonus for good structure
            if len(paragraphs) > 3:
                readability_score += 0.1
            
            return max(0.0, min(1.0, readability_score))
            
        except Exception as e:
            logger.error(f"Error checking readability: {e}")
            return 0.7  # Default score
    
    async def _improve_readability(self, content: str) -> str:
        """Improve content readability"""
        try:
            prompt = f"""
            Improve the readability of the following content:
            
            Content:
            {content}
            
            Please:
            1. Break down long sentences
            2. Use shorter paragraphs
            3. Add clear headings and subheadings
            4. Use bullet points where appropriate
            5. Make the language more accessible
            6. Maintain the original message and tone
            
            Return the improved content.
            """
            
            improved_content = await self.ai_client.generate_text(prompt, max_tokens=2000)
            return improved_content
            
        except Exception as e:
            logger.error(f"Error improving readability: {e}")
            return content
    
    async def optimize_strategy(self, analytics: Dict, startup_info: Dict, 
                              current_config: Dict) -> Dict:
        """
        Optimize content strategy based on analytics
        
        Args:
            analytics: Analytics data from published content
            startup_info: Information about the startup
            current_config: Current content configuration
            
        Returns:
            Optimization recommendations
        """
        logger.info("Generating content strategy optimizations")
        
        try:
            # Analyze performance data
            performance_analysis = await self._analyze_performance(analytics)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                performance_analysis, startup_info, current_config
            )
            
            # Create optimization plan
            optimization_plan = await self._create_optimization_plan(
                recommendations, current_config
            )
            
            return {
                'performance_analysis': performance_analysis,
                'recommendations': recommendations,
                'optimization_plan': optimization_plan,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing strategy: {e}")
            return {'error': str(e)}
    
    async def _analyze_performance(self, analytics: Dict) -> Dict:
        """Analyze content performance data"""
        try:
            # Extract key metrics
            total_posts = len(analytics.get('posts', []))
            avg_engagement = analytics.get('average_engagement', 0)
            top_performing_content = analytics.get('top_performing', [])
            platform_performance = analytics.get('platform_performance', {})
            
            # Calculate performance insights
            insights = {
                'total_posts': total_posts,
                'average_engagement': avg_engagement,
                'best_performing_platforms': [],
                'content_themes_performance': {},
                'optimal_posting_times': [],
                'engagement_trends': 'stable'
            }
            
            # Analyze platform performance
            if platform_performance:
                sorted_platforms = sorted(
                    platform_performance.items(),
                    key=lambda x: x[1].get('engagement', 0),
                    reverse=True
                )
                insights['best_performing_platforms'] = [p[0] for p in sorted_platforms[:3]]
            
            # Analyze content themes
            if top_performing_content:
                themes = {}
                for post in top_performing_content:
                    theme = post.get('theme', 'general')
                    themes[theme] = themes.get(theme, 0) + 1
                insights['content_themes_performance'] = themes
            
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {}
    
    async def _generate_recommendations(self, performance_analysis: Dict, 
                                      startup_info: Dict, current_config: Dict) -> List[Dict]:
        """Generate optimization recommendations"""
        try:
            recommendations = []
            
            # Platform recommendations
            if performance_analysis.get('best_performing_platforms'):
                recommendations.append({
                    'type': 'platform_focus',
                    'title': 'Focus on High-Performing Platforms',
                    'description': f"Concentrate content efforts on: {', '.join(performance_analysis['best_performing_platforms'])}",
                    'priority': 'high',
                    'impact': 'high'
                })
            
            # Content theme recommendations
            if performance_analysis.get('content_themes_performance'):
                top_themes = sorted(
                    performance_analysis['content_themes_performance'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                
                recommendations.append({
                    'type': 'content_themes',
                    'title': 'Optimize Content Themes',
                    'description': f"Increase content in these themes: {', '.join([t[0] for t in top_themes])}",
                    'priority': 'medium',
                    'impact': 'medium'
                })
            
            # Posting frequency recommendations
            current_frequency = current_config.get('blog_frequency', 2)
            if performance_analysis.get('average_engagement', 0) < 0.5:
                recommendations.append({
                    'type': 'posting_frequency',
                    'title': 'Adjust Posting Frequency',
                    'description': f"Consider reducing frequency to focus on quality over quantity",
                    'priority': 'medium',
                    'impact': 'medium'
                })
            
            # Content quality recommendations
            recommendations.append({
                'type': 'content_quality',
                'title': 'Enhance Content Quality',
                'description': "Focus on creating more engaging and valuable content",
                'priority': 'high',
                'impact': 'high'
            })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def _create_optimization_plan(self, recommendations: List[Dict], 
                                      current_config: Dict) -> Dict:
        """Create an actionable optimization plan"""
        try:
            plan = {
                'short_term_actions': [],
                'medium_term_actions': [],
                'long_term_actions': [],
                'metrics_to_track': [],
                'timeline': '4 weeks'
            }
            
            # Categorize recommendations by timeline
            for rec in recommendations:
                if rec['priority'] == 'high':
                    plan['short_term_actions'].append(rec)
                elif rec['priority'] == 'medium':
                    plan['medium_term_actions'].append(rec)
                else:
                    plan['long_term_actions'].append(rec)
            
            # Add metrics to track
            plan['metrics_to_track'] = [
                'engagement_rate',
                'reach',
                'clicks',
                'shares',
                'comments',
                'follower_growth'
            ]
            
            return plan
            
        except Exception as e:
            logger.error(f"Error creating optimization plan: {e}")
            return {}
    
    async def generate_seo_recommendations(self, content: str, topic: str) -> Dict:
        """
        Generate SEO recommendations for content
        
        Args:
            content: The content to analyze
            topic: The content topic
            
        Returns:
            SEO recommendations
        """
        logger.info(f"Generating SEO recommendations for topic: {topic}")
        
        try:
            # Analyze content for SEO
            seo_analysis = await self._analyze_seo_content(content, topic)
            
            # Generate keyword recommendations
            keyword_recommendations = await self._generate_keyword_recommendations(topic)
            
            # Generate meta tag recommendations
            meta_recommendations = await self._generate_meta_recommendations(topic, content)
            
            return {
                'seo_score': seo_analysis.get('score', 0),
                'keyword_recommendations': keyword_recommendations,
                'meta_recommendations': meta_recommendations,
                'content_improvements': seo_analysis.get('improvements', []),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating SEO recommendations: {e}")
            return {'error': str(e)}
    
    async def _analyze_seo_content(self, content: str, topic: str) -> Dict:
        """Analyze content for SEO factors"""
        try:
            # Basic SEO analysis
            words = content.lower().split()
            word_count = len(words)
            
            # Check for keyword density
            topic_words = topic.lower().split()
            keyword_density = {}
            for word in topic_words:
                if len(word) > 3:  # Skip short words
                    density = words.count(word) / word_count
                    keyword_density[word] = density
            
            # Check for headings
            headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
            
            # Check for links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            # Calculate SEO score
            seo_score = 0.0
            
            # Word count score
            if 800 <= word_count <= 2000:
                seo_score += 0.3
            elif 500 <= word_count < 800:
                seo_score += 0.2
            
            # Keyword density score
            if any(density > 0.01 for density in keyword_density.values()):
                seo_score += 0.2
            
            # Headings score
            if len(headings) >= 3:
                seo_score += 0.2
            
            # Links score
            if len(links) >= 2:
                seo_score += 0.1
            
            # Structure score
            if '\n\n' in content:  # Has paragraphs
                seo_score += 0.2
            
            improvements = []
            if seo_score < 0.7:
                if word_count < 800:
                    improvements.append("Increase content length to at least 800 words")
                if not any(density > 0.01 for density in keyword_density.values()):
                    improvements.append("Include more relevant keywords naturally")
                if len(headings) < 3:
                    improvements.append("Add more headings and subheadings")
                if len(links) < 2:
                    improvements.append("Include relevant internal and external links")
            
            return {
                'score': seo_score,
                'word_count': word_count,
                'keyword_density': keyword_density,
                'headings': headings,
                'links': links,
                'improvements': improvements
            }
            
        except Exception as e:
            logger.error(f"Error analyzing SEO content: {e}")
            return {'score': 0.5, 'improvements': ['Error analyzing content']}
    
    async def _generate_keyword_recommendations(self, topic: str) -> List[str]:
        """Generate keyword recommendations for the topic"""
        try:
            prompt = f"""
            Generate 10 relevant SEO keywords for the topic: "{topic}"
            
            Requirements:
            - Include long-tail keywords
            - Mix of high and medium search volume
            - Relevant to startup and business audience
            - Include industry-specific terms
            
            Return only the keywords, one per line.
            """
            
            response = await self.ai_client.generate_text(prompt, max_tokens=500)
            
            # Parse keywords
            keywords = [line.strip() for line in response.split('\n') if line.strip()]
            return keywords[:10]  # Limit to 10 keywords
            
        except Exception as e:
            logger.error(f"Error generating keyword recommendations: {e}")
            return []
    
    async def _generate_meta_recommendations(self, topic: str, content: str) -> Dict:
        """Generate meta tag recommendations"""
        try:
            # Generate title
            title_prompt = f"""
            Create an SEO-optimized title tag for: "{topic}"
            
            Requirements:
            - 50-60 characters
            - Include main keyword
            - Compelling and clickable
            - Relevant to startup audience
            
            Return only the title.
            """
            
            title = await self.ai_client.generate_text(title_prompt, max_tokens=100)
            
            # Generate description
            desc_prompt = f"""
            Create an SEO-optimized meta description for: "{topic}"
            
            Content preview:
            {content[:200]}...
            
            Requirements:
            - 150-160 characters
            - Include main keyword
            - Compelling and descriptive
            - Include call-to-action
            
            Return only the description.
            """
            
            description = await self.ai_client.generate_text(desc_prompt, max_tokens=200)
            
            return {
                'title': title.strip(),
                'description': description.strip(),
                'keywords': await self._generate_keyword_recommendations(topic)
            }
            
        except Exception as e:
            logger.error(f"Error generating meta recommendations: {e}")
            return {}
    
    def _enforce_twitter_limit(self, content: str, max_length: int = 280) -> str:
        """
        Enforce Twitter character limit with smart truncation
        
        Args:
            content: The content to check and truncate if needed
            max_length: Maximum allowed characters (default 280)
            
        Returns:
            Content within character limit
        """
        if len(content) <= max_length:
            return content
            
        logger.warning(f"Twitter content too long ({len(content)} chars), truncating to {max_length}")
        
        # Smart truncation - try to end at sentence boundary
        if max_length > 20:
            truncated = content[:max_length-3]
            
            # Try to end at sentence boundary
            last_sentence = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
            if last_sentence > max_length * 0.7:  # If sentence boundary is reasonable
                return truncated[:last_sentence+1]
            
            # Try to end at word boundary  
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:  # If word boundary is reasonable
                return truncated[:last_space] + "..."
            
            # Last resort - hard truncate with ellipsis
            return truncated + "..."
        else:
            # For very short limits, just truncate
            return content[:max_length]
    
    def _enforce_platform_limits(self, content: str, platform: str) -> str:
        """
        Enforce platform-specific character limits
        
        Args:
            content: The content to check and truncate if needed
            platform: Target platform
            
        Returns:
            Content within platform limits
        """
        platform_limits = {
            'twitter': 280,
            'linkedin': 3000,
            'facebook': 63206,
            'instagram': 2200
        }
        
        max_length = platform_limits.get(platform.lower(), 280)  # Default to Twitter limit
        
        if len(content) <= max_length:
            return content
            
        logger.warning(f"{platform} content too long ({len(content)} chars), truncating to {max_length}")
        
        # For Twitter, use special handling
        if platform.lower() == 'twitter':
            return self._enforce_twitter_limit(content, max_length)
        
        # For other platforms, use simpler truncation since they have more space
        if max_length > 50:
            truncated = content[:max_length-3]
            
            # Try to end at paragraph boundary for longer content
            last_paragraph = truncated.rfind('\n\n')
            if last_paragraph > max_length * 0.8:
                return truncated[:last_paragraph]
                
            # Try to end at sentence boundary
            last_sentence = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
            if last_sentence > max_length * 0.9:
                return truncated[:last_sentence+1]
            
            # End at word boundary
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.95:
                return truncated[:last_space] + "..."
            
            return truncated + "..."
        else:
            return content[:max_length] 