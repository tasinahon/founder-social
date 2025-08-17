#!/usr/bin/env python3
"""
Founder Socials AI Agent - Main Application

Entry point for the AI agent with both web interface and CLI support.
"""

import asyncio
import argparse
import uvicorn
from pathlib import Path
from typing import Dict, Any
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

# from agent.founder_socials_agent import FounderSocialsAgent
from agent.core import FounderSocialsAgent
from ui.dashboard import create_dashboard_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FounderSocialsApp:
    """Main application class for Founder Socials AI Agent."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.agent = None
        self.web_app = None
    
    async def initialize(self):
        """Initialize the AI agent and web application."""
        try:
            logger.info("Initializing Founder Socials AI Agent...")
            self.agent = FounderSocialsAgent(self.config_path)
            await self.agent.initialize()
            
            # Create web dashboard
            self.web_app = create_dashboard_app(self.agent)
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            raise
    
    async def run_web_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the web dashboard server."""
        if not self.web_app:
            await self.initialize()
        
        # Get port from environment variable if available (for deployment platforms)
        port = int(os.getenv('PORT', port))
        
        logger.info(f"Starting web server on {host}:{port}")
        config = uvicorn.Config(
            app=self.web_app,
            host=host,
            port=port,
            log_level="info",
            reload=False
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    async def run_cli_command(self, command: str, **kwargs):
        """Run a CLI command."""
        if not self.agent:
            await self.initialize()
        
        try:
            if command == "plan":
                weeks = kwargs.get('weeks', 4)
                logger.info(f"Planning content calendar for {weeks} weeks...")
                calendar = await self.agent.plan_content_calendar(weeks)
                logger.info("Content calendar generated successfully")
                return calendar
            
            elif command == "generate":
                topic = kwargs.get('topic')
                content_type = kwargs.get('content_type', 'blog')
                platform = kwargs.get('platform', 'general')
                
                if not topic:
                    raise ValueError("Topic is required for generate command")
                
                logger.info(f"Generating {content_type} content for topic: {topic}")
                task = self.agent.create_content_task(
                    topic=topic,
                    content_type=content_type,
                    platform=platform
                )
                result = await self.agent.generate_content(task)
                logger.info("Content generated successfully")
                return result
            
            elif command == "publish":
                content_id = kwargs.get('content_id')
                auto_publish = kwargs.get('auto_publish', True)
                
                if content_id:
                    # Publish specific content
                    logger.info(f"Publishing content with ID: {content_id}")
                    # Implementation would load content by ID and publish
                    pass
                else:
                    # Run full pipeline
                    logger.info("Running full content pipeline...")
                    result = await self.agent.run_content_pipeline(auto_publish)
                    logger.info("Content pipeline completed")
                    return result
            
            elif command == "analytics":
                days = kwargs.get('days', 30)
                logger.info(f"Generating analytics report for last {days} days...")
                report = await self.agent.get_analytics_report(days)
                logger.info("Analytics report generated")
                return report
            
            elif command == "optimize":
                logger.info("Optimizing content strategy...")
                result = await self.agent.optimize_content_strategy()
                logger.info("Content strategy optimized")
                return result
            
            else:
                raise ValueError(f"Unknown command: {command}")
                
        except Exception as e:
            logger.error(f"Error running command '{command}': {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the application gracefully."""
        if self.agent:
            await self.agent.shutdown()
        logger.info("Application shutdown complete")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Founder Socials AI Agent")
    parser.add_argument("--config", default="config/config.yaml", help="Configuration file path")
    parser.add_argument("--mode", choices=["web", "cli"], default="web", help="Run mode")
    parser.add_argument("--host", default="0.0.0.0", help="Web server host")
    parser.add_argument("--port", type=int, default=8000, help="Web server port")
    
    # CLI commands
    parser.add_argument("--command", help="CLI command to run")
    parser.add_argument("--topic", help="Content topic for generate command")
    parser.add_argument("--content-type", choices=["blog", "social"], default="blog", help="Content type")
    parser.add_argument("--platform", default="general", help="Target platform")
    parser.add_argument("--weeks", type=int, default=4, help="Number of weeks for planning")
    parser.add_argument("--days", type=int, default=30, help="Number of days for analytics")
    parser.add_argument("--auto-publish", action="store_true", help="Auto-publish content")
    
    args = parser.parse_args()
    
    app = FounderSocialsApp(args.config)
    
    try:
        if args.mode == "web":
            await app.run_web_server(args.host, args.port)
        elif args.mode == "cli":
            if not args.command:
                print("Error: Command is required for CLI mode")
                parser.print_help()
                return
            
            result = await app.run_cli_command(
                args.command,
                topic=args.topic,
                content_type=args.content_type,
                platform=args.platform,
                weeks=args.weeks,
                days=args.days,
                auto_publish=args.auto_publish
            )
            
            if result:
                print("Result:", result)
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

# For deployment platforms that expect an 'app' object
try:
    from agent.core import FounderSocialsAgent
    from ui.dashboard import create_dashboard_app
    
    # Create a simple app instance for deployment
    _agent = FounderSocialsAgent()
    app = create_dashboard_app(_agent)
except Exception as e:
    logger.warning(f"Could not create app instance for deployment: {e}")
    app = None 