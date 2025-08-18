"""
Founder Socials AI Agent - Web Dashboard

FastAPI-based web interface for the AI agent.
"""

from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import asyncio
import json
import os
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from agent.core import FounderSocialsAgent, ContentTask
from agent.social_auth import SocialAuthManager

# Configure logging to show detailed logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # This will show logs in the terminal
    ]
)

logger = logging.getLogger(__name__)

def _generate_content_title(topic: str, content_type: str, platform: str, content: str) -> str:
    """Generate a meaningful title for saved content"""
    
    # Clean up the topic
    if topic and topic.strip():
        cleaned_topic = topic.strip()
        cleaned_topic = re.sub(r'^(Write about|Create|Generate|Post about|Topic:)\s*', '', cleaned_topic, flags=re.IGNORECASE)
        cleaned_topic = re.sub(r'[^\w\s-]', '', cleaned_topic)
        cleaned_topic = re.sub(r'\s+', ' ', cleaned_topic).strip()
        
        if len(cleaned_topic) > 50:
            cleaned_topic = cleaned_topic[:47] + "..."
            
        if cleaned_topic:
            return f"{cleaned_topic} ({platform} {content_type})"
    
    # Extract from content if no good topic
    if content and content.strip():
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            line = re.sub(r'^[#*\-\s]+', '', line)
            line = re.sub(r'^\*\*.*?\*\*:?\s*', '', line)
            
            if line and len(line) > 10:
                title = line[:40]
                if len(line) > 40:
                    title += "..."
                return f"{title} ({platform} {content_type})"
    
    # Fallback to timestamp
    timestamp = datetime.now().strftime("%m/%d %H:%M")
    return f"{platform.title()} {content_type} - {timestamp}"

def _generate_content_preview(content: str) -> str:
    """Generate a preview of the content"""
    if not content:
        return "No content"
    
    preview = content.strip()
    preview = re.sub(r'\*\*.*?\*\*', '', preview)  # Remove bold
    preview = re.sub(r'^#{1,6}\s*', '', preview, flags=re.MULTILINE)  # Remove headers
    preview = re.sub(r'\n+', ' ', preview)  # Collapse newlines
    preview = preview[:100]
    if len(content) > 100:
        preview += "..."
    return preview

logger = logging.getLogger(__name__)


def create_dashboard_app(agent: FounderSocialsAgent) -> FastAPI:
    """Create and configure the FastAPI dashboard application."""
    
    app = FastAPI(
        title="Founder Socials AI Agent",
        description="AI-powered content creation and publishing for startups",
        version="1.0.0"
    )
    
    # Initialize social auth manager
    social_auth = SocialAuthManager(agent.config)
    
    # Setup templates and static files
    templates_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    
    templates = Jinja2Templates(directory=str(templates_dir))
    
    # Mount static files
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard_home(request: Request):
        """Main dashboard page."""
        try:
            # Get recent analytics
            analytics = await agent.get_analytics_report(days=7)
            
            # Get current calendar
            calendar = await agent.mcp_manager.load_calendar()
            
            return templates.TemplateResponse(
                "dashboard.html",
                {
                    "request": request,
                    "startup_name": agent.config.get("startup", {}).get("name", "Your Startup"),
                    "analytics": analytics,
                    "calendar": calendar
                }
            )
        except Exception as e:
            logger.error(f"Error loading dashboard: {e}")
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": str(e)}
            )
    
    @app.get("/plan", response_class=HTMLResponse)
    async def plan_content_page(request: Request):
        """Content planning page."""
        return templates.TemplateResponse(
            "plan.html",
            {"request": request}
        )
    
    @app.post("/plan/generate")
    async def generate_content_plan(
        request: Request,
        weeks: int = Form(4),
        blog_frequency: int = Form(2),
        social_frequency: int = Form(5)
    ):
        """Generate content plan."""
        try:
            calendar = await agent.plan_content_calendar(weeks)
            return JSONResponse(content=calendar)
        except Exception as e:
            logger.error(f"Error generating content plan: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/create", response_class=HTMLResponse)
    async def create_content_page(request: Request):
        """Content creation page."""
        return templates.TemplateResponse(
            "create.html",
            {"request": request}
        )
    
    @app.post("/create/generate")
    async def generate_content(
        request: Request,
        topic: str = Form(...),
        content_type: str = Form("blog"),
        platform: str = Form("general")
    ):
        """Generate content for a topic."""
        try:
            task = agent.create_content_task(
                topic=topic,
                content_type=content_type,
                platform=platform
            )
            result = await agent.generate_content(task)
            
            # Generate meaningful title for the content
            title = _generate_content_title(topic, content_type, platform, result.content)
            
            # Enhanced metadata with better naming
            enhanced_metadata = {
                'topic': result.topic,
                'platform': result.platform,
                'status': 'draft',
                'title': title,
                'display_name': title[:60] + "..." if len(title) > 60 else title,
                'preview': _generate_content_preview(result.content),
                'word_count': len(result.content.split()) if result.content else 0,
                'char_count': len(result.content) if result.content else 0,
                'created_display': datetime.now().strftime("%m/%d/%Y at %I:%M %p"),
                'keywords': result.metadata.get('keywords', []),
                'reading_time': result.metadata.get('reading_time'),
            }
            
            # Auto-save generated content as draft with enhanced metadata
            await agent.mcp_manager.save_content(
                content_id=result.id,
                content=result.content,
                content_type=result.type,
                metadata=enhanced_metadata
            )
            
            # Convert ContentTask to JSON-serializable dict
            result_dict = {
                "id": result.id,
                "type": result.type,
                "platform": result.platform,
                "topic": result.topic,
                "status": result.status,
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "scheduled_for": result.scheduled_for.isoformat() if result.scheduled_for else None,
                "content": result.content,
                "metadata": result.metadata or {}
            }
            
            return JSONResponse(content=result_dict)
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/publish", response_class=HTMLResponse)
    async def publish_content_page(request: Request):
        """Content publishing page."""
        return templates.TemplateResponse(
            "publish.html",
            {"request": request}
        )
    
    @app.post("/create/save")
    async def save_draft(
        request: Request,
        content_id: str = Form(...),
        topic: str = Form(...),
        content_type: str = Form(...),
        platform: str = Form(...),
        content: str = Form(...),
        metadata: Optional[str] = Form(None)
    ):
        """Save content as draft."""
        try:
            # Parse metadata if provided
            metadata_dict = {}
            if metadata:
                try:
                    metadata_dict = json.loads(metadata)
                except:
                    pass
            
            # Save content using MCP manager
            success = await agent.mcp_manager.save_content(
                content_id=content_id,
                content=content,
                content_type=content_type,
                metadata={
                    **metadata_dict,
                    'topic': topic,
                    'platform': platform,
                    'status': 'draft'
                }
            )
            
            return JSONResponse(content={"success": success, "message": "Draft saved successfully!"})
        except Exception as e:
            logger.error(f"Error saving draft: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/create/drafts")
    async def get_drafts():
        """Get all saved drafts with enhanced display information."""
        try:
            data_path = agent.mcp_manager.file_system_config.get('root_path', './data')
            content_dir = os.path.join(data_path, 'content')
            
            drafts = []
            if os.path.exists(content_dir):
                for filename in os.listdir(content_dir):
                    if filename.endswith('.json'):
                        content_path = os.path.join(content_dir, filename)
                        with open(content_path, 'r') as f:
                            content_data = json.load(f)
                            if content_data.get('metadata', {}).get('status') == 'draft':
                                # Enhance draft data for better display
                                metadata = content_data.get('metadata', {})
                                
                                # If no title, generate one
                                if not metadata.get('title'):
                                    title = _generate_content_title(
                                        metadata.get('topic', ''),
                                        content_data.get('type', 'content'),
                                        metadata.get('platform', 'general'),
                                        content_data.get('content', '')
                                    )
                                    metadata['title'] = title
                                    metadata['display_name'] = title[:60] + "..." if len(title) > 60 else title
                                
                                # Add preview if missing
                                if not metadata.get('preview'):
                                    metadata['preview'] = _generate_content_preview(content_data.get('content', ''))
                                
                                # Add counts if missing
                                if not metadata.get('word_count'):
                                    content = content_data.get('content', '')
                                    metadata['word_count'] = len(content.split()) if content else 0
                                    metadata['char_count'] = len(content) if content else 0
                                
                                content_data['metadata'] = metadata
                                drafts.append(content_data)
            
            # Sort by creation date (newest first)
            drafts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return JSONResponse(content={"drafts": drafts})
        except Exception as e:
            logger.error(f"Error getting drafts: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/publish/content")
    async def publish_content(
        request: Request,
        content_id: str = Form(...),
        platforms: List[str] = Form(...),
        linkedin_mode: Optional[str] = Form(None)
    ):
        """Publish content to specified platforms."""
        try:
            # DEBUG: Log the incoming request
            print(f"\n🔍 WEB INTERFACE DEBUG:")
            print(f"   Content ID: {content_id}")
            print(f"   Platforms: {platforms}")
            print(f"   LinkedIn Mode: {linkedin_mode}")
            
            # Load content from file system
            content_data = await agent.mcp_manager.load_content(content_id)
            if not content_data:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # DEBUG: Log the content data
            print(f"   Content Data: {content_data}")
            print(f"   Content Length: {len(content_data.get('content', ''))}")
            print(f"   Content Type: {content_data.get('type', 'unknown')}")
            
            # Create ContentTask for publishing
            from agent.core import ContentTask
            import uuid
            from datetime import datetime
            
            task = ContentTask(
                id=content_id,
                type=content_data.get('type', 'blog'),
                platform=platforms[0] if platforms else 'general',
                topic=content_data.get('metadata', {}).get('topic', ''),
                status='ready',
                content=content_data.get('content', ''),
                metadata=content_data.get('metadata', {}),
                created_at=datetime.now(),
                scheduled_for=None
            )
            
            # DEBUG: Log the task details
            print(f"   Task Content: '{task.content}'")
            print(f"   Task Type: {task.type}")
            print(f"   Task Metadata: {task.metadata}")
            print(f"   Task Platform: {task.platform}")
            print(f"🚀 About to call agent.publish_content()...")
            
            # Add LinkedIn posting mode to metadata if specified
            if linkedin_mode and 'linkedin' in platforms:
                task.metadata['linkedin_posting_mode'] = linkedin_mode
            
            # Publish to each platform
            success_count = 0
            for platform in platforms:
                task.platform = platform
                if await agent.publish_content(task):
                    success_count += 1
            
            success = success_count > 0
            result = {
                "success": success, 
                "published_platforms": success_count,
                "total_platforms": len(platforms)
            }
            
            # Include LinkedIn mode in response for user feedback
            if linkedin_mode and 'linkedin' in platforms:
                result['linkedin_mode'] = linkedin_mode
            
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"Error publishing content: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/publish/content-with-images")
    async def publish_content_with_images(
        request: Request,
        content: str = Form(...),
        platforms: str = Form(...),
        content_type: str = Form("social"),
        images: List = None
    ):
        """Publish content with images to specified platforms."""
        try:
            import tempfile
            import os
            
            # Parse platforms from JSON string
            import json
            platform_list = json.loads(platforms)
            
            logger.info(f"Publishing content with images to platforms: {platform_list}")
            logger.info(f"Content length: {len(content)}")
            
            # Handle uploaded images
            image_paths = []
            if images:
                # Get files from the request
                form = await request.form()
                uploaded_files = form.getlist("images")
                
                for uploaded_file in uploaded_files:
                    if uploaded_file.filename:
                        # Save uploaded file temporarily
                        temp_dir = tempfile.mkdtemp()
                        file_path = os.path.join(temp_dir, uploaded_file.filename)
                        
                        with open(file_path, "wb") as buffer:
                            buffer.write(await uploaded_file.read())
                        
                        image_paths.append(file_path)
                        logger.info(f"Saved uploaded image: {file_path}")
            
            logger.info(f"Processing {len(image_paths)} images")
            
            # Publish to each platform with images
            success_count = 0
            total_platforms = len(platform_list)
            
            for platform in platform_list:
                try:
                    logger.info(f"Publishing to {platform} with {len(image_paths)} images")
                    
                    # Use the enhanced publisher with image support
                    result = await agent.publisher.publish(
                        content=content,
                        platform=platform,
                        content_type=content_type,
                        images=image_paths if image_paths else None
                    )
                    
                    if result:
                        success_count += 1
                        logger.info(f"✅ Successfully published to {platform}")
                    else:
                        logger.error(f"❌ Failed to publish to {platform}")
                        
                except Exception as e:
                    logger.error(f"Error publishing to {platform}: {e}")
                    continue
            
            # Clean up temporary files
            for file_path in image_paths:
                try:
                    os.unlink(file_path)
                    os.rmdir(os.path.dirname(file_path))
                except Exception as e:
                    logger.warning(f"Could not clean up temp file {file_path}: {e}")
            
            success = success_count > 0
            result = {
                "success": success,
                "published_platforms": success_count,
                "total_platforms": total_platforms,
                "platforms": platform_list,
                "images_uploaded": len(image_paths)
            }
            
            logger.info(f"Publishing result: {result}")
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"Error publishing content with images: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/analytics", response_class=HTMLResponse)
    async def analytics_page(request: Request):
        """Analytics dashboard page."""
        try:
            analytics = await agent.get_analytics_report(days=30)
            return templates.TemplateResponse(
                "analytics.html",
                {"request": request, "analytics": analytics}
            )
        except Exception as e:
            logger.error(f"Error loading analytics: {e}")
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": str(e)}
            )
    
    @app.get("/api/analytics")
    async def get_analytics_api(days: int = 30):
        """API endpoint for analytics data."""
        try:
            analytics = await agent.get_analytics_report(days)
            return JSONResponse(content=analytics)
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/optimize", response_class=HTMLResponse)
    async def optimize_page(request: Request):
        """Content optimization page."""
        return templates.TemplateResponse(
            "optimize.html",
            {"request": request}
        )
    
    @app.post("/optimize/strategy")
    async def optimize_strategy(request: Request):
        """Optimize content strategy."""
        try:
            result = await agent.optimize_content_strategy()
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"Error optimizing strategy: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Social Media Authentication Endpoints
    @app.get("/auth/{platform}/connect")
    async def connect_platform(request: Request, platform: str):
        """Initiate OAuth connection for a platform."""
        try:
            auth_url, state = social_auth.get_auth_url(platform)
            return RedirectResponse(url=auth_url)
        except Exception as e:
            logger.error(f"Error initiating OAuth for {platform}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/auth/{platform}/callback")
    async def oauth_callback(
        request: Request,
        platform: str,
        code: str = None,
        state: str = None,
        error: str = None
    ):
        """Handle OAuth callback from social media platforms."""
        if error:
            logger.error(f"OAuth error for {platform}: {error}")
            return templates.TemplateResponse(
                "auth_error.html",
                {"request": request, "platform": platform, "error": error}
            )
        
        if not code or not state:
            raise HTTPException(status_code=400, detail="Missing OAuth parameters")
        
        try:
            result = await social_auth.handle_callback(platform, code, state)
            
            if result['success']:
                return templates.TemplateResponse(
                    "auth_success.html",
                    {
                        "request": request,
                        "platform": platform,
                        "profile": result.get('profile', {})
                    }
                )
            else:
                return templates.TemplateResponse(
                    "auth_error.html",
                    {
                        "request": request,
                        "platform": platform,
                        "error": result.get('error', 'Unknown error')
                    }
                )
        except Exception as e:
            logger.error(f"Error handling OAuth callback for {platform}: {e}")
            return templates.TemplateResponse(
                "auth_error.html",
                {"request": request, "platform": platform, "error": str(e)}
            )
    
    @app.post("/auth/{platform}/disconnect")
    async def disconnect_platform(request: Request, platform: str):
        """Disconnect a social media platform."""
        try:
            success = social_auth.disconnect_platform(platform)
            return JSONResponse(content={"success": success})
        except Exception as e:
            logger.error(f"Error disconnecting {platform}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/auth/status")
    async def get_auth_status():
        """Get authentication status for all platforms."""
        try:
            status = social_auth.get_connection_status()
            return JSONResponse(content=status)
        except Exception as e:
            logger.error(f"Error getting auth status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page(request: Request):
        """Settings page."""
        try:
            # Get connection status for all platforms
            connection_status = social_auth.get_connection_status()
            configured_platforms = social_auth.get_configured_platforms()
            
            return templates.TemplateResponse(
                "settings.html",
                {
                    "request": request,
                    "config": agent.config,
                    "connection_status": connection_status,
                    "configured_platforms": configured_platforms
                }
            )
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": str(e)}
            )
    
    @app.post("/settings/update")
    async def update_settings(request: Request):
        """Update settings."""
        try:
            # This would update the configuration
            return JSONResponse(content={"success": True})
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return JSONResponse(content={"status": "healthy", "timestamp": datetime.now().isoformat()})
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """Handle 404 errors."""
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=404
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        """Handle 500 errors."""
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(exc)},
            status_code=500
        )
    
    return app

# Initialize the app at module level for uvicorn
import os
from agent.core import FounderSocialsAgent

# Create agent instance for the dashboard
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
agent = FounderSocialsAgent(config_path)
app = create_dashboard_app(agent) 