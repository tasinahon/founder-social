"""
Analytics for Founder Socials AI Agent

This module handles content performance tracking and analytics reporting.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class Analytics:
    """
    Handles content analytics and performance tracking
    """
    
    def __init__(self, config: Dict):
        """Initialize the analytics module"""
        self.config = config
        self.analytics_config = config.get('analytics', {})
        
        # Storage for analytics data
        self.performance_data = []
        self.published_content = []
        
        logger.info("Analytics module initialized")
    
    async def track_publication(self, content_task) -> bool:
        """
        Track a content publication
        
        Args:
            content_task: The content task that was published
            
        Returns:
            True if tracking successful, False otherwise
        """
        logger.info(f"Tracking publication for task {content_task.id}")
        
        try:
            # Create tracking record
            tracking_record = {
                'task_id': content_task.id,
                'platform': content_task.platform,
                'content_type': content_task.type,
                'topic': content_task.topic,
                'published_at': datetime.now().isoformat(),
                'content_length': len(content_task.content) if content_task.content else 0,
                'metadata': content_task.metadata or {},
                'performance_metrics': {
                    'likes': 0,
                    'shares': 0,
                    'comments': 0,
                    'clicks': 0,
                    'reach': 0,
                    'engagement_rate': 0.0
                }
            }
            
            # Store tracking record
            self.published_content.append(tracking_record)
            
            # Schedule performance update
            await self._schedule_performance_update(content_task.id)
            
            logger.info(f"Publication tracking started for task {content_task.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking publication: {e}")
            return False
    
    async def _schedule_performance_update(self, task_id: str):
        """Schedule performance metrics update"""
        try:
            # In a real implementation, this would schedule API calls to get metrics
            # For now, simulate performance data after a delay
            await asyncio.sleep(5)  # Simulate delay
            
            # Generate simulated performance data
            performance_data = await self._generate_simulated_performance(task_id)
            
            # Update tracking record
            for record in self.published_content:
                if record['task_id'] == task_id:
                    record['performance_metrics'] = performance_data
                    record['last_updated'] = datetime.now().isoformat()
                    break
            
            logger.info(f"Performance data updated for task {task_id}")
            
        except Exception as e:
            logger.error(f"Error updating performance data: {e}")
    
    async def _generate_simulated_performance(self, task_id: str) -> Dict:
        """Generate simulated performance metrics"""
        import random
        
        # Generate realistic performance data based on platform and content type
        base_metrics = {
            'likes': random.randint(10, 200),
            'shares': random.randint(2, 50),
            'comments': random.randint(1, 20),
            'clicks': random.randint(50, 500),
            'reach': random.randint(500, 5000),
            'engagement_rate': random.uniform(0.02, 0.08)
        }
        
        # Adjust based on platform
        platform_multipliers = {
            'twitter': {'likes': 1.2, 'shares': 1.5, 'comments': 1.3},
            'linkedin': {'likes': 1.0, 'shares': 1.8, 'comments': 1.6},
            'facebook': {'likes': 1.5, 'shares': 1.2, 'comments': 1.4},
            'instagram': {'likes': 1.8, 'shares': 0.8, 'comments': 1.1}
        }
        
        # Apply platform adjustments
        for record in self.published_content:
            if record['task_id'] == task_id:
                platform = record['platform']
                if platform in platform_multipliers:
                    multipliers = platform_multipliers[platform]
                    for metric, multiplier in multipliers.items():
                        if metric in base_metrics:
                            base_metrics[metric] = int(base_metrics[metric] * multiplier)
                break
        
        return base_metrics
    
    async def generate_report(self, published_content: List, days: int = 30) -> Dict:
        """
        Generate analytics report
        
        Args:
            published_content: List of published content
            days: Number of days to analyze
            
        Returns:
            Analytics report dictionary
        """
        logger.info(f"Generating analytics report for last {days} days")
        
        try:
            # Filter content by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_content = [
                content for content in published_content
                if datetime.fromisoformat(content.published_at) >= cutoff_date
            ]
            
            # Calculate metrics
            total_posts = len(recent_content)
            total_engagement = sum(
                content.metadata.get('performance_metrics', {}).get('likes', 0) +
                content.metadata.get('performance_metrics', {}).get('shares', 0) +
                content.metadata.get('performance_metrics', {}).get('comments', 0)
                for content in recent_content
            )
            
            # Platform performance
            platform_performance = {}
            for content in recent_content:
                platform = content.platform
                if platform not in platform_performance:
                    platform_performance[platform] = {
                        'posts': 0,
                        'total_engagement': 0,
                        'avg_engagement': 0
                    }
                
                platform_performance[platform]['posts'] += 1
                engagement = (
                    content.metadata.get('performance_metrics', {}).get('likes', 0) +
                    content.metadata.get('performance_metrics', {}).get('shares', 0) +
                    content.metadata.get('performance_metrics', {}).get('comments', 0)
                )
                platform_performance[platform]['total_engagement'] += engagement
            
            # Calculate averages
            for platform in platform_performance:
                posts = platform_performance[platform]['posts']
                total_eng = platform_performance[platform]['total_engagement']
                platform_performance[platform]['avg_engagement'] = total_eng / posts if posts > 0 else 0
            
            # Top performing content
            top_performing = sorted(
                recent_content,
                key=lambda x: (
                    x.metadata.get('performance_metrics', {}).get('likes', 0) +
                    x.metadata.get('performance_metrics', {}).get('shares', 0) +
                    x.metadata.get('performance_metrics', {}).get('comments', 0)
                ),
                reverse=True
            )[:5]
            
            # Content type performance
            content_type_performance = {}
            for content in recent_content:
                content_type = content.type
                if content_type not in content_type_performance:
                    content_type_performance[content_type] = {
                        'posts': 0,
                        'total_engagement': 0,
                        'avg_engagement': 0
                    }
                
                content_type_performance[content_type]['posts'] += 1
                engagement = (
                    content.metadata.get('performance_metrics', {}).get('likes', 0) +
                    content.metadata.get('performance_metrics', {}).get('shares', 0) +
                    content.metadata.get('performance_metrics', {}).get('comments', 0)
                )
                content_type_performance[content_type]['total_engagement'] += engagement
            
            # Calculate content type averages
            for content_type in content_type_performance:
                posts = content_type_performance[content_type]['posts']
                total_eng = content_type_performance[content_type]['total_engagement']
                content_type_performance[content_type]['avg_engagement'] = total_eng / posts if posts > 0 else 0
            
            # Generate insights
            insights = await self._generate_insights(
                platform_performance, content_type_performance, top_performing
            )
            
            report = {
                'period': f"Last {days} days",
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_posts': total_posts,
                    'total_engagement': total_engagement,
                    'average_engagement_per_post': total_engagement / total_posts if total_posts > 0 else 0
                },
                'platform_performance': platform_performance,
                'content_type_performance': content_type_performance,
                'top_performing_content': [
                    {
                        'id': content.id,
                        'topic': content.topic,
                        'platform': content.platform,
                        'type': content.type,
                        'engagement': (
                            content.metadata.get('performance_metrics', {}).get('likes', 0) +
                            content.metadata.get('performance_metrics', {}).get('shares', 0) +
                            content.metadata.get('performance_metrics', {}).get('comments', 0)
                        )
                    }
                    for content in top_performing
                ],
                'insights': insights,
                'recommendations': await self._generate_recommendations(
                    platform_performance, content_type_performance
                )
            }
            
            logger.info(f"Analytics report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {'error': str(e)}
    
    async def _generate_insights(self, platform_performance: Dict, 
                               content_type_performance: Dict, 
                               top_performing: List) -> List[str]:
        """Generate insights from performance data"""
        insights = []
        
        try:
            # Platform insights
            if platform_performance:
                best_platform = max(
                    platform_performance.items(),
                    key=lambda x: x[1]['avg_engagement']
                )
                insights.append(f"Best performing platform: {best_platform[0]} with {best_platform[1]['avg_engagement']:.1f} avg engagement")
            
            # Content type insights
            if content_type_performance:
                best_type = max(
                    content_type_performance.items(),
                    key=lambda x: x[1]['avg_engagement']
                )
                insights.append(f"Best performing content type: {best_type[0]} with {best_type[1]['avg_engagement']:.1f} avg engagement")
            
            # Top content insights
            if top_performing:
                top_content = top_performing[0]
                insights.append(f"Top performing content: '{top_content.topic}' on {top_content.platform}")
            
            # Engagement trends
            total_engagement = sum(p['total_engagement'] for p in platform_performance.values())
            if total_engagement > 1000:
                insights.append("Strong overall engagement performance")
            elif total_engagement > 500:
                insights.append("Moderate engagement performance")
            else:
                insights.append("Opportunity to improve engagement")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["Unable to generate insights"]
    
    async def _generate_recommendations(self, platform_performance: Dict, 
                                      content_type_performance: Dict) -> List[Dict]:
        """Generate recommendations based on performance data"""
        recommendations = []
        
        try:
            # Platform recommendations
            if platform_performance:
                worst_platform = min(
                    platform_performance.items(),
                    key=lambda x: x[1]['avg_engagement']
                )
                recommendations.append({
                    'type': 'platform',
                    'title': f'Improve {worst_platform[0]} performance',
                    'description': f'Focus on improving engagement on {worst_platform[0]}',
                    'priority': 'medium'
                })
            
            # Content type recommendations
            if content_type_performance:
                worst_type = min(
                    content_type_performance.items(),
                    key=lambda x: x[1]['avg_engagement']
                )
                recommendations.append({
                    'type': 'content',
                    'title': f'Optimize {worst_type[0]} content',
                    'description': f'Improve engagement for {worst_type[0]} content',
                    'priority': 'high'
                })
            
            # General recommendations
            recommendations.extend([
                {
                    'type': 'general',
                    'title': 'Increase posting frequency',
                    'description': 'Consider posting more frequently to increase reach',
                    'priority': 'medium'
                },
                {
                    'type': 'general',
                    'title': 'Engage with audience',
                    'description': 'Respond to comments and engage with followers',
                    'priority': 'high'
                }
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def get_real_time_metrics(self, task_id: str) -> Dict:
        """
        Get real-time metrics for a specific content piece
        
        Args:
            task_id: The task ID to get metrics for
            
        Returns:
            Real-time metrics dictionary
        """
        logger.info(f"Getting real-time metrics for task {task_id}")
        
        try:
            # Find the content record
            content_record = None
            for record in self.published_content:
                if record['task_id'] == task_id:
                    content_record = record
                    break
            
            if not content_record:
                return {'error': 'Content not found'}
            
            # Get current metrics
            metrics = content_record.get('performance_metrics', {})
            
            # Calculate engagement rate
            total_engagement = metrics.get('likes', 0) + metrics.get('shares', 0) + metrics.get('comments', 0)
            reach = metrics.get('reach', 1)
            engagement_rate = (total_engagement / reach) * 100 if reach > 0 else 0
            
            return {
                'task_id': task_id,
                'platform': content_record['platform'],
                'content_type': content_record['content_type'],
                'published_at': content_record['published_at'],
                'metrics': {
                    **metrics,
                    'engagement_rate_percent': round(engagement_rate, 2),
                    'total_engagement': total_engagement
                },
                'last_updated': content_record.get('last_updated', content_record['published_at'])
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {'error': str(e)}
    
    async def export_analytics_data(self, format: str = 'json') -> str:
        """
        Export analytics data
        
        Args:
            format: Export format (json, csv)
            
        Returns:
            Exported data as string
        """
        logger.info(f"Exporting analytics data in {format} format")
        
        try:
            if format.lower() == 'json':
                return json.dumps({
                    'published_content': self.published_content,
                    'performance_data': self.performance_data,
                    'exported_at': datetime.now().isoformat()
                }, indent=2)
            elif format.lower() == 'csv':
                # Generate CSV format
                csv_lines = ['task_id,platform,content_type,topic,published_at,likes,shares,comments,clicks,reach,engagement_rate']
                
                for record in self.published_content:
                    metrics = record.get('performance_metrics', {})
                    csv_lines.append(
                        f"{record['task_id']},{record['platform']},{record['content_type']},"
                        f"\"{record['topic']}\",{record['published_at']},"
                        f"{metrics.get('likes', 0)},{metrics.get('shares', 0)},{metrics.get('comments', 0)},"
                        f"{metrics.get('clicks', 0)},{metrics.get('reach', 0)},{metrics.get('engagement_rate', 0)}"
                    )
                
                return '\n'.join(csv_lines)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            return f"Error: {str(e)}" 