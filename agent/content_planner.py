"""
Content Planner for Founder Socials AI Agent

This module handles content planning, idea generation, and editorial calendar creation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random
import uuid

from .ai_client import AIClient

logger = logging.getLogger(__name__)

class ContentPlanner:
    """
    Handles content planning and editorial calendar generation
    """
    
    def __init__(self, config: Dict):
        """Initialize the content planner"""
        self.config = config
        self.ai_client = AIClient(config.get('ai', {}))
        self.content_themes = config.get('content', {}).get('content_themes', [])
        self.hashtags = config.get('content', {}).get('hashtags', [])
        
        logger.info("Content Planner initialized")
    
    async def generate_calendar(self, startup_info: Dict, weeks_ahead: int = 4, 
                              blog_frequency: int = 2, social_frequency: int = 5) -> Dict:
        """
        Generate a comprehensive content calendar
        
        Args:
            startup_info: Information about the startup
            weeks_ahead: Number of weeks to plan
            blog_frequency: Blog posts per week
            social_frequency: Social posts per week
            
        Returns:
            Dictionary containing the content calendar
        """
        logger.info(f"Generating content calendar for {weeks_ahead} weeks")
        
        try:
            # Generate content ideas
            content_ideas = await self._generate_content_ideas(startup_info)
            
            # Create editorial calendar
            calendar = await self._create_editorial_calendar(
                content_ideas=content_ideas,
                weeks_ahead=weeks_ahead,
                blog_frequency=blog_frequency,
                social_frequency=social_frequency,
                startup_info=startup_info
            )
            
            return calendar
            
        except Exception as e:
            logger.error(f"Error generating content calendar: {e}")
            raise
    
    async def _generate_content_ideas(self, startup_info: Dict) -> List[Dict]:
        """
        Generate content ideas based on startup information and themes
        
        Args:
            startup_info: Information about the startup
            
        Returns:
            List of content ideas with topics and descriptions
        """
        logger.info("Generating content ideas")
        
        try:
            # Create prompt for content idea generation
            prompt = self._create_content_ideas_prompt(startup_info)
            
            # Generate ideas using AI
            response = await self.ai_client.generate_text(prompt)
            
            # Parse the response to extract content ideas
            content_ideas = self._parse_content_ideas(response)
            
            # Add variety and ensure we have enough ideas
            content_ideas.extend(self._generate_fallback_ideas(startup_info))
            
            logger.info(f"Generated {len(content_ideas)} content ideas")
            return content_ideas
            
        except Exception as e:
            logger.error(f"Error generating content ideas: {e}")
            return self._generate_fallback_ideas(startup_info)
    
    def _create_content_ideas_prompt(self, startup_info: Dict) -> str:
        """Create a prompt for generating content ideas"""
        return f"""
        You are a content strategist for a startup. Generate 20 engaging content ideas for blog posts and social media posts.
        
        Startup Information:
        - Name: {startup_info.get('name', 'Unknown')}
        - Industry: {startup_info.get('industry', 'Technology')}
        - Description: {startup_info.get('description', 'A technology startup')}
        - Target Audience: {startup_info.get('target_audience', 'Startup founders')}
        - Brand Voice: {startup_info.get('brand_voice', 'Professional and innovative')}
        
        Content Themes to Focus On:
        {', '.join(self.content_themes)}
        
        Generate content ideas that are:
        1. Relevant to the startup's industry and audience
        2. Engaging and shareable
        3. Educational or informative
        4. Aligned with the brand voice
        5. Suitable for both blog posts and social media
        
        For each idea, provide:
        - Topic title
        - Brief description (1-2 sentences)
        - Content type (blog, social, or both)
        - Target platform (if social)
        - Key message or takeaway
        
        Format your response as a structured list that can be easily parsed.
        """
    
    def _parse_content_ideas(self, ai_response: str) -> List[Dict]:
        """Parse AI response to extract content ideas"""
        ideas = []
        
        try:
            # Simple parsing - in a real implementation, you'd use more sophisticated parsing
            lines = ai_response.split('\n')
            current_idea = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Topic:') or line.startswith('Title:'):
                    if current_idea:
                        ideas.append(current_idea)
                    current_idea = {'topic': line.split(':', 1)[1].strip()}
                elif line.startswith('Description:'):
                    current_idea['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('Type:'):
                    current_idea['type'] = line.split(':', 1)[1].strip()
                elif line.startswith('Platform:'):
                    current_idea['platform'] = line.split(':', 1)[1].strip()
                elif line.startswith('Message:'):
                    current_idea['message'] = line.split(':', 1)[1].strip()
            
            if current_idea:
                ideas.append(current_idea)
                
        except Exception as e:
            logger.error(f"Error parsing content ideas: {e}")
        
        return ideas
    
    def _generate_fallback_ideas(self, startup_info: Dict) -> List[Dict]:
        """Generate fallback content ideas if AI generation fails"""
        industry = startup_info.get('industry', 'Technology').lower()
        
        fallback_ideas = [
            {
                'topic': f'How {startup_info.get("name", "Our Startup")} is Revolutionizing {industry}',
                'description': f'An in-depth look at how we\'re changing the {industry} landscape',
                'type': 'blog',
                'platform': 'wordpress',
                'message': 'Innovation and disruption in our industry'
            },
            {
                'topic': f'5 Key Lessons We Learned Building a {industry} Startup',
                'description': 'Insights and learnings from our startup journey',
                'type': 'blog',
                'platform': 'wordpress',
                'message': 'Sharing valuable lessons with the community'
            },
            {
                'topic': f'Behind the Scenes: A Day in the Life at {startup_info.get("name", "Our Startup")}',
                'description': 'See what it\'s really like to work at our startup',
                'type': 'social',
                'platform': 'linkedin',
                'message': 'Transparency and team culture'
            },
            {
                'topic': f'Customer Success Story: How We Helped [Client]',
                'description': 'Real results and impact from our customers',
                'type': 'both',
                'platform': 'twitter',
                'message': 'Customer success and value delivery'
            },
            {
                'topic': f'Industry Trends: What\'s Next in {industry}',
                'description': 'Our predictions and insights on industry trends',
                'type': 'blog',
                'platform': 'wordpress',
                'message': 'Thought leadership and industry expertise'
            }
        ]
        
        return fallback_ideas
    
    async def _create_editorial_calendar(self, content_ideas: List[Dict], weeks_ahead: int,
                                       blog_frequency: int, social_frequency: int,
                                       startup_info: Dict) -> Dict:
        """
        Create an editorial calendar with scheduled content
        
        Args:
            content_ideas: List of content ideas
            weeks_ahead: Number of weeks to plan
            blog_frequency: Blog posts per week
            social_frequency: Social posts per week
            startup_info: Startup information
            
        Returns:
            Editorial calendar dictionary
        """
        logger.info("Creating editorial calendar")
        
        try:
            calendar = {
                'startup_info': startup_info,
                'planning_period': f"{weeks_ahead} weeks",
                'generated_at': datetime.now().isoformat(),
                'tasks': []
            }
            
            # Calculate total content needed
            total_blog_posts = weeks_ahead * blog_frequency
            total_social_posts = weeks_ahead * social_frequency
            
            # Distribute content ideas across the calendar
            blog_ideas = [idea for idea in content_ideas if idea.get('type') in ['blog', 'both']]
            social_ideas = [idea for idea in content_ideas if idea.get('type') in ['social', 'both']]
            
            # Schedule blog posts
            blog_schedule = self._schedule_content(
                ideas=blog_ideas,
                total_needed=total_blog_posts,
                weeks_ahead=weeks_ahead,
                frequency=blog_frequency,
                content_type='blog'
            )
            
            # Schedule social posts
            social_schedule = self._schedule_content(
                ideas=social_ideas,
                total_needed=total_social_posts,
                weeks_ahead=weeks_ahead,
                frequency=social_frequency,
                content_type='social'
            )
            
            # Combine and sort all tasks
            all_tasks = blog_schedule + social_schedule
            all_tasks.sort(key=lambda x: x['scheduled_for'])
            
            calendar['tasks'] = all_tasks
            
            logger.info(f"Editorial calendar created with {len(all_tasks)} tasks")
            return calendar
            
        except Exception as e:
            logger.error(f"Error creating editorial calendar: {e}")
            raise
    
    def _schedule_content(self, ideas: List[Dict], total_needed: int, weeks_ahead: int,
                         frequency: int, content_type: str) -> List[Dict]:
        """
        Schedule content across the specified time period
        
        Args:
            ideas: List of content ideas
            total_needed: Total number of content pieces needed
            weeks_ahead: Number of weeks to plan
            frequency: Posts per week
            content_type: Type of content (blog or social)
            
        Returns:
            List of scheduled content tasks
        """
        tasks = []
        start_date = datetime.now()
        
        # Ensure we have enough ideas
        while len(ideas) < total_needed:
            ideas.extend(ideas[:total_needed - len(ideas)])
        
        # Shuffle ideas for variety
        random.shuffle(ideas)
        
        # Schedule content
        for i in range(total_needed):
            # Calculate scheduled date
            week = i // frequency
            day_in_week = i % frequency
            
            # Schedule on different days of the week
            scheduled_date = start_date + timedelta(weeks=week, days=day_in_week)
            
            # Add some time variation within the day
            hour = 9 + (i % 3) * 3  # 9 AM, 12 PM, or 3 PM
            scheduled_date = scheduled_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            idea = ideas[i]
            
            task = {
                'id': str(uuid.uuid4()),
                'type': content_type,
                'platform': idea.get('platform', 'wordpress' if content_type == 'blog' else 'twitter'),
                'topic': idea['topic'],
                'description': idea.get('description', ''),
                'message': idea.get('message', ''),
                'scheduled_for': scheduled_date.isoformat(),
                'status': 'planned',
                'hashtags': self._select_hashtags(idea),
                'estimated_engagement': self._estimate_engagement(idea)
            }
            
            tasks.append(task)
        
        return tasks
    
    def _select_hashtags(self, idea: Dict) -> List[str]:
        """Select relevant hashtags for the content idea"""
        selected_hashtags = []
        
        # Add general startup hashtags
        selected_hashtags.extend(['#startup', '#entrepreneurship'])
        
        # Add industry-specific hashtags
        industry = self.config.get('startup', {}).get('industry', 'Technology').lower()
        if 'tech' in industry or 'technology' in industry:
            selected_hashtags.append('#tech')
        elif 'fintech' in industry:
            selected_hashtags.append('#fintech')
        elif 'health' in industry:
            selected_hashtags.append('#healthtech')
        
        # Add content-specific hashtags
        topic = idea.get('topic', '').lower()
        if 'lesson' in topic or 'learn' in topic:
            selected_hashtags.append('#lessonslearned')
        elif 'customer' in topic or 'success' in topic:
            selected_hashtags.append('#customersuccess')
        elif 'trend' in topic or 'future' in topic:
            selected_hashtags.append('#trends')
        
        # Limit to 5 hashtags
        return selected_hashtags[:5]
    
    def _estimate_engagement(self, idea: Dict) -> Dict:
        """Estimate potential engagement for the content"""
        base_engagement = {
            'likes': 50,
            'shares': 10,
            'comments': 5,
            'clicks': 100
        }
        
        # Adjust based on content type and topic
        topic = idea.get('topic', '').lower()
        
        if 'customer' in topic or 'success' in topic:
            base_engagement['likes'] *= 1.5
            base_engagement['shares'] *= 1.3
        elif 'lesson' in topic or 'learn' in topic:
            base_engagement['likes'] *= 1.2
            base_engagement['comments'] *= 1.5
        elif 'trend' in topic or 'future' in topic:
            base_engagement['shares'] *= 1.4
            base_engagement['clicks'] *= 1.3
        
        return base_engagement
    
    async def research_trending_topics(self, industry: str) -> List[Dict]:
        """
        Research trending topics in the industry
        
        Args:
            industry: Industry to research
            
        Returns:
            List of trending topics
        """
        logger.info(f"Researching trending topics in {industry}")
        
        try:
            # Create research prompt
            prompt = f"""
            Research and identify the top 10 trending topics in the {industry} industry right now.
            
            For each topic, provide:
            - Topic name
            - Why it's trending
            - Potential content angles
            - Target audience
            - Estimated engagement potential
            
            Focus on topics that would be relevant for a startup in this industry.
            """
            
            # Generate research using AI
            response = await self.ai_client.generate_text(prompt)
            
            # Parse trending topics
            trending_topics = self._parse_trending_topics(response)
            
            logger.info(f"Found {len(trending_topics)} trending topics")
            return trending_topics
            
        except Exception as e:
            logger.error(f"Error researching trending topics: {e}")
            return []
    
    def _parse_trending_topics(self, ai_response: str) -> List[Dict]:
        """Parse AI response to extract trending topics"""
        topics = []
        
        try:
            lines = ai_response.split('\n')
            current_topic = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Topic:') or line.startswith('Name:'):
                    if current_topic:
                        topics.append(current_topic)
                    current_topic = {'name': line.split(':', 1)[1].strip()}
                elif line.startswith('Trending:'):
                    current_topic['trending_reason'] = line.split(':', 1)[1].strip()
                elif line.startswith('Angles:'):
                    current_topic['content_angles'] = line.split(':', 1)[1].strip()
                elif line.startswith('Audience:'):
                    current_topic['target_audience'] = line.split(':', 1)[1].strip()
                elif line.startswith('Engagement:'):
                    current_topic['engagement_potential'] = line.split(':', 1)[1].strip()
            
            if current_topic:
                topics.append(current_topic)
                
        except Exception as e:
            logger.error(f"Error parsing trending topics: {e}")
        
        return topics 