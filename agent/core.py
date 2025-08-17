"""
Core AI Agent for Founder Socials

This module contains the main agent class that orchestrates content creation,
planning, optimization, and publishing across multiple platforms.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import yaml
import os

from .content_planner import ContentPlanner
from .content_generator import ContentGenerator
from .content_optimizer import ContentOptimizer
from .publisher import Publisher
from .analytics import Analytics
from .mcp_manager import MCPManager

logger = logging.getLogger(__name__)

@dataclass
class ContentTask:
    """Represents a content creation task"""
    id: str
    type: str  # 'blog' or 'social'
    platform: str
    topic: str
    status: str  # 'planned', 'draft', 'review', 'published'
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    content: Optional[str] = None
    metadata: Optional[Dict] = None

class FounderSocialsAgent:
    """
    Main AI Agent for startup content creation and publishing
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the agent with configuration"""
        self.config = self._load_config(config_path)
        self.mcp_manager = MCPManager(self.config.get('mcp', {}))
        
        # Initialize components
        self.content_planner = ContentPlanner(self.config)
        self.content_generator = ContentGenerator(self.config)
        self.content_optimizer = ContentOptimizer(self.config)
        self.publisher = Publisher(self.config)
        self.analytics = Analytics(self.config)
        
        # State management
        self.content_queue: List[ContentTask] = []
        self.published_content: List[ContentTask] = []
        
        logger.info("Founder Socials AI Agent initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'ai': {
                'provider': 'openai',
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.7
            },
            'startup': {
                'name': 'Your Startup',
                'industry': 'Technology',
                'description': 'A technology startup',
                'target_audience': 'Startup founders',
                'brand_voice': 'Professional and innovative'
            },
            'content': {
                'blog_frequency': 2,
                'social_frequency': 5,
                'content_themes': ['Product updates', 'Industry insights']
            }
        }
    
    async def plan_content_calendar(self, weeks_ahead: int = 4) -> Dict:
        """
        Generate a content calendar for the specified number of weeks
        
        Args:
            weeks_ahead: Number of weeks to plan ahead
            
        Returns:
            Dictionary containing the content calendar
        """
        logger.info(f"Planning content calendar for {weeks_ahead} weeks")
        
        try:
            # Get startup context
            startup_info = self.config.get('startup', {})
            
            # Plan content using the content planner
            calendar = await self.content_planner.generate_calendar(
                startup_info=startup_info,
                weeks_ahead=weeks_ahead,
                blog_frequency=self.config['content']['blog_frequency'],
                social_frequency=self.config['content']['social_frequency']
            )
            
            # Store calendar in MCP file system
            await self.mcp_manager.save_calendar(calendar)
            
            logger.info(f"Content calendar generated successfully")
            return calendar
            
        except Exception as e:
            logger.error(f"Error planning content calendar: {e}")
            raise
    
    def create_content_task(self, topic: str, content_type: str = "blog", platform: str = "general") -> ContentTask:
        """
        Create a new content task
        
        Args:
            topic: The topic for the content
            content_type: Type of content ('blog', 'social', 'thread', 'article')
            platform: Target platform ('twitter', 'linkedin', 'facebook', 'general')
            
        Returns:
            ContentTask object ready for content generation
        """
        import uuid
        
        task = ContentTask(
            id=str(uuid.uuid4()),
            type=content_type,
            platform=platform,
            topic=topic,
            status="planned",
            created_at=datetime.now(),
            content=None,
            metadata={}
        )
        
        logger.info(f"Created content task: {task.id} for topic '{topic}' ({content_type}, {platform})")
        return task
    
    async def generate_content(self, task: ContentTask) -> ContentTask:
        """
        Generate content for a specific task
        
        Args:
            task: ContentTask object with topic and platform info
            
        Returns:
            Updated ContentTask with generated content
        """
        logger.info(f"Generating content for task {task.id}: {task.topic}")
        
        try:
            # Generate content based on type and platform
            if task.type == 'blog':
                content = await self.content_generator.generate_blog_post(
                    topic=task.topic,
                    startup_info=self.config.get('startup', {}),
                    template_config=self.config.get('templates', {}).get('blog_post', {})
                )
            else:  # social post
                content = await self.content_generator.generate_social_post(
                    topic=task.topic,
                    platform=task.platform,
                    startup_info=self.config.get('startup', {}),
                    template_config=self.config.get('templates', {}).get('social_post', {})
                )
            
            # Optimize content
            optimized_content = await self.content_optimizer.optimize_content(
                content=content,
                platform=task.platform,
                content_type=task.type
            )
            
            # Update task with generated content
            task.content = optimized_content
            task.status = 'draft'
            task.metadata = {
                'generated_at': datetime.now().isoformat(),
                'word_count': len(optimized_content.split()),
                'platform': task.platform
            }
            
            logger.info(f"Content generated successfully for task {task.id}")
            return task
            
        except Exception as e:
            logger.error(f"Error generating content for task {task.id}: {e}")
            task.status = 'error'
            task.metadata = {'error': str(e)}
            return task
    
    async def publish_content(self, task: ContentTask) -> bool:
        """
        Publish content to the specified platform
        
        Args:
            task: ContentTask with content ready for publishing
            
        Returns:
            True if published successfully, False otherwise
        """
        logger.info(f"Publishing content for task {task.id} to {task.platform}")
        
        try:
            # Publish content
            success = await self.publisher.publish(
                content=task.content,
                platform=task.platform,
                content_type=task.type,
                metadata=task.metadata
            )
            
            if success:
                task.status = 'published'
                task.metadata['published_at'] = datetime.now().isoformat()
                self.published_content.append(task)
                
                # Track analytics
                await self.analytics.track_publication(task)
                
                logger.info(f"Content published successfully to {task.platform}")
                return True
            else:
                task.status = 'publish_failed'
                logger.error(f"Failed to publish content to {task.platform}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing content: {e}")
            task.status = 'error'
            task.metadata['error'] = str(e)
            return False
    
    async def run_content_pipeline(self, auto_publish: bool = True) -> Dict:
        """
        Run the complete content pipeline: plan, generate, and publish
        
        Args:
            auto_publish: Whether to automatically publish content
            
        Returns:
            Dictionary with pipeline results
        """
        logger.info("Starting content pipeline")
        
        results = {
            'planned': 0,
            'generated': 0,
            'published': 0,
            'errors': 0,
            'tasks': []
        }
        
        try:
            # 1. Plan content calendar
            calendar = await self.plan_content_calendar(weeks_ahead=2)
            results['planned'] = len(calendar.get('tasks', []))
            
            # 2. Generate content for each task
            for task_data in calendar.get('tasks', []):
                task = ContentTask(
                    id=task_data['id'],
                    type=task_data['type'],
                    platform=task_data['platform'],
                    topic=task_data['topic'],
                    status='planned',
                    created_at=datetime.now(),
                    scheduled_for=datetime.fromisoformat(task_data['scheduled_for'])
                )
                
                # Generate content
                task = await self.generate_content(task)
                if task.status == 'draft':
                    results['generated'] += 1
                else:
                    results['errors'] += 1
                
                results['tasks'].append(task)
                
                # 3. Publish if auto_publish is enabled
                if auto_publish and task.status == 'draft':
                    success = await self.publish_content(task)
                    if success:
                        results['published'] += 1
                    else:
                        results['errors'] += 1
            
            logger.info(f"Content pipeline completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in content pipeline: {e}")
            results['errors'] += 1
            return results
    
    async def get_analytics_report(self, days: int = 30) -> Dict:
        """
        Get analytics report for published content
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with analytics data
        """
        logger.info(f"Generating analytics report for last {days} days")
        
        try:
            report = await self.analytics.generate_report(
                published_content=self.published_content,
                days=days
            )
            
            # Store report in MCP file system
            await self.mcp_manager.save_analytics_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {'error': str(e)}
    
    async def optimize_content_strategy(self) -> Dict:
        """
        Analyze performance and suggest content strategy optimizations
        
        Returns:
            Dictionary with optimization recommendations
        """
        logger.info("Generating content strategy optimizations")
        
        try:
            # Get recent analytics
            analytics = await self.get_analytics_report(days=30)
            
            # Generate optimization recommendations
            recommendations = await self.content_optimizer.optimize_strategy(
                analytics=analytics,
                startup_info=self.config.get('startup', {}),
                current_config=self.config.get('content', {})
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error optimizing content strategy: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Cleanup and shutdown the agent"""
        logger.info("Shutting down Founder Socials AI Agent")
        
        try:
            # Close MCP connections
            await self.mcp_manager.close()
            
            # Save final state
            await self._save_state()
            
            logger.info("Agent shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def _save_state(self):
        """Save current agent state"""
        state = {
            'content_queue': [task.__dict__ for task in self.content_queue],
            'published_content': [task.__dict__ for task in self.published_content],
            'last_updated': datetime.now().isoformat()
        }
        
        await self.mcp_manager.save_state(state) 