"""
Founder Socials AI Agent - Web Dashboard

FastAPI-based web interface for the AI agent.
"""

from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks, UploadFile, Depends
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
from agent.user_settings import user_settings_manager
from agent.auth import user_manager, get_current_user, get_current_user_optional

# Try to import advanced content generator
try:
    from agent.advanced_content_generator import (
        AdvancedContentGenerator, WritingStyle, TargetAudience, 
        ContentTone, ContentPurpose
    )
    ADVANCED_GENERATOR_AVAILABLE = True
except ImportError:
    print("⚠️  Advanced content generator not available")
    ADVANCED_GENERATOR_AVAILABLE = False

# Configure logging to show detailed logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # This will show logs in the terminal
    ]
)

logger = logging.getLogger(__name__)

# Background task for token management
async def background_token_management():
    """Background task to check and renew tokens"""
    while True:
        try:
            logger.info("Running background token management...")
            
            # Import Facebook token manager
            try:
                from agent.facebook_token_manager import auto_token_manager
                await auto_token_manager.background_token_check(user_settings_manager)
            except ImportError:
                logger.warning("Facebook token manager not available for background task")
            
            # Wait 1 hour before next check
            await asyncio.sleep(3600)
            
        except Exception as e:
            logger.error(f"Error in background token management: {e}")
            # Wait 10 minutes before retrying
            await asyncio.sleep(600)

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
    
    # Start background token management task
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting background token management...")
        asyncio.create_task(background_token_management())
    
    # Initialize social auth manager
    social_auth = SocialAuthManager(agent.config)
    
    # Setup templates and static files
    templates_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    
    templates = Jinja2Templates(directory=str(templates_dir))
    
    # Mount static files
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Authentication routes
    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        """Login page."""
        return templates.TemplateResponse("login.html", {"request": request})
    
    @app.get("/register", response_class=HTMLResponse)
    async def register_page(request: Request):
        """Registration page."""
        return templates.TemplateResponse("register.html", {"request": request})
    
    @app.post("/auth/register")
    async def register_user(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        company: str = Form(None)
    ):
        """Register a new user."""
        try:
            result = user_manager.create_user(email, password, name, company)
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return JSONResponse(
                content={"success": False, "detail": str(e)},
                status_code=500
            )
    
    @app.post("/auth/login")
    async def login_user(
        request: Request,
        email: str = Form(...),
        password: str = Form(...)
    ):
        """Authenticate user and create session."""
        try:
            user = user_manager.authenticate_user(email, password)
            if not user:
                return JSONResponse(
                    content={"success": False, "detail": "Invalid email or password"},
                    status_code=401
                )
            
            # Create access token
            access_token = user_manager.create_access_token(data={"sub": user["email"]})
            
            response = JSONResponse(content={
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "user": user
            })
            
            # Set cookie for automatic authentication
            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age=30 * 24 * 60 * 60,  # 30 days
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax"
            )
            
            return response
        except Exception as e:
            logger.error(f"Login error: {e}")
            return JSONResponse(
                content={"success": False, "detail": str(e)},
                status_code=500
            )
    
    @app.post("/auth/demo-login")
    async def demo_login(request: Request):
        """Create a demo user session."""
        try:
            # Create or get demo user
            demo_email = "demo@foundersocials.com"
            demo_user = user_manager.authenticate_user(demo_email, "demo123")
            
            if not demo_user:
                # Create demo user if it doesn't exist
                result = user_manager.create_user(
                    email=demo_email,
                    password="demo123",
                    name="Demo User",
                    company="Demo Company"
                )
                if result["success"]:
                    demo_user = user_manager.authenticate_user(demo_email, "demo123")
            
            if demo_user:
                access_token = user_manager.create_access_token(data={"sub": demo_user["email"]})
                
                response = JSONResponse(content={
                    "success": True,
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": demo_user
                })
                
                # Set cookie for automatic authentication
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    max_age=30 * 24 * 60 * 60,  # 30 days
                    httponly=True,
                    secure=False,  # Set to True in production with HTTPS
                    samesite="lax"
                )
                
                return response
            else:
                return JSONResponse(
                    content={"success": False, "detail": "Failed to create demo user"},
                    status_code=500
                )
        except Exception as e:
            logger.error(f"Demo login error: {e}")
            return JSONResponse(
                content={"success": False, "detail": str(e)},
                status_code=500
            )
    
    @app.get("/auth/logout")
    async def logout_user(request: Request):
        """Logout user."""
        return RedirectResponse(url="/login", status_code=302)
    
    # Protected route example
    @app.get("/profile")
    async def user_profile(request: Request, current_user: dict = Depends(get_current_user)):
        """User profile page (protected)."""
        stats = user_manager.get_user_stats(current_user["id"])
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": current_user,
                "stats": stats
            }
        )
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard_home(request: Request, current_user: dict = Depends(get_current_user_optional)):
        """Main dashboard page."""
        try:
            # Redirect to login if not authenticated
            if not current_user:
                return RedirectResponse(url="/login", status_code=302)
            
            # Get recent analytics
            analytics = await agent.get_analytics_report(days=7)
            
            # Get current calendar
            calendar = await agent.mcp_manager.load_calendar()
            
            # Get user statistics
            stats = user_manager.get_user_stats(current_user["id"])
            
            return templates.TemplateResponse(
                "dashboard.html",
                {
                    "request": request,
                    "startup_name": current_user.get("company", "Your Startup"),
                    "analytics": analytics,
                    "calendar": calendar,
                    "user": current_user,
                    "stats": stats
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
    
    @app.post("/create/generate-advanced")
    async def generate_advanced_content(
        request: Request,
        topic: str = Form(...),
        content_type: str = Form("social"),
        platform: str = Form("general"),
        writing_style: str = Form("informative"),
        target_audience: str = Form("startup_founders"),
        content_tone: str = Form("professional"),
        content_purpose: str = Form("educate"),
        content_length: str = Form("medium"),
        include_data: str = Form("false"),
        thread_length: Optional[str] = Form("5")
    ):
        """Generate advanced content with professional customization."""
        try:
            if not ADVANCED_GENERATOR_AVAILABLE:
                # Fallback to basic generation
                return await generate_content(request, topic, content_type, platform)
            
            # Initialize advanced content generator
            advanced_generator = AdvancedContentGenerator(agent.config)
            
            # Convert string enums to proper enum values
            try:
                style_enum = WritingStyle(writing_style)
                audience_enum = TargetAudience(target_audience)
                tone_enum = ContentTone(content_tone)
                purpose_enum = ContentPurpose(content_purpose)
            except ValueError as e:
                logger.warning(f"Invalid enum value: {e}, using defaults")
                style_enum = WritingStyle.INFORMATIVE
                audience_enum = TargetAudience.STARTUP_FOUNDERS
                tone_enum = ContentTone.PROFESSIONAL
                purpose_enum = ContentPurpose.EDUCATE
            
            # Prepare additional options
            additional_options = {
                'content_length': content_length,
                'include_data': include_data.lower() == 'true',
                'thread_length': int(thread_length) if content_type == 'thread' else 5
            }
            
            # Generate advanced content
            result = await advanced_generator.generate_advanced_content(
                topic=topic,
                platform=platform,
                content_type=content_type,
                writing_style=style_enum,
                target_audience=audience_enum,
                content_tone=tone_enum,
                content_purpose=purpose_enum,
                additional_options=additional_options
            )
            
            # Generate unique ID for this content
            content_id = f"content_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Generate title
            title = _generate_content_title(topic, content_type, platform, result['content'])
            
            # Enhanced metadata
            enhanced_metadata = {
                'topic': topic,
                'platform': platform,
                'status': 'draft',
                'title': title,
                'display_name': title[:60] + "..." if len(title) > 60 else title,
                'preview': _generate_content_preview(result['content']),
                'word_count': result.get('word_count', 0),
                'char_count': result.get('character_count', 0),
                'created_display': datetime.now().strftime("%m/%d/%Y at %I:%M %p"),
                'writing_style': writing_style,
                'target_audience': target_audience,
                'content_tone': content_tone,
                'content_purpose': content_purpose,
                'engagement_score': result.get('engagement_score', 0),
                'estimated_read_time': result.get('estimated_read_time', 0),
                'generator_version': 'advanced_2.0'
            }
            
            # Auto-save as draft
            await agent.mcp_manager.save_content(
                content_id=content_id,
                content=result['content'],
                content_type=content_type,
                metadata=enhanced_metadata
            )
            
            # Prepare response
            response_data = {
                "id": content_id,
                "content": result['content'],
                "content_type": content_type,
                "platform": platform,
                "topic": topic,
                "metadata": result['metadata'],
                "word_count": result.get('word_count', 0),
                "character_count": result.get('character_count', 0),
                "estimated_read_time": result.get('estimated_read_time', 0),
                "engagement_score": result.get('engagement_score', 0),
                "suggestions": result.get('suggestions', []),
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Advanced content generated successfully: {len(result['content'])} chars")
            return JSONResponse(content=response_data)
            
        except Exception as e:
            logger.error(f"Error generating advanced content: {e}")
            # Fallback to basic generation on error
            return await generate_content(request, topic, content_type, platform)
    
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
        linkedin_mode: Optional[str] = Form(None),
        current_user: dict = Depends(get_current_user)
    ):
        """Publish content to specified platforms."""
        try:
            # DEBUG: Log the incoming request
            print(f"\n🔍 WEB INTERFACE DEBUG:")
            print(f"   Content ID: {content_id}")
            print(f"   Platforms: {platforms}")
            print(f"   LinkedIn Mode: {linkedin_mode}")
            
            user_email = current_user["email"]
            
            # Check credentials for all requested platforms BEFORE publishing
            credential_check = user_settings_manager.check_multiple_platforms(user_email, platforms)
            
            if not credential_check['can_publish']:
                logger.warning(f"User {user_email} attempted to publish without proper credentials")
                return JSONResponse(
                    content={
                        "success": False,
                        "error": "Missing platform credentials",
                        "message": "Please configure your platform credentials before publishing.",
                        "issues": credential_check['issues'],
                        "ready_platforms": credential_check['ready_platforms'],
                        "redirect_to_settings": True
                    },
                    status_code=400
                )
            
            # If there are some issues but some platforms are ready, warn but allow publishing
            if credential_check['issues']:
                logger.warning(f"Some platforms have credential issues for user {user_email}: {credential_check['issues']}")
            
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
            
            # Get user-specific publisher
            user_publisher = agent.get_user_publisher(user_email)
            
            # Only publish to platforms that are ready
            ready_platforms = credential_check['ready_platforms']
            results = {}
            success_count = 0
            
            for platform in platforms:
                if platform not in ready_platforms:
                    # Skip platforms with credential issues
                    platform_issue = next((issue for issue in credential_check['issues'] if issue['platform'] == platform), None)
                    results[platform] = {
                        "success": False, 
                        "error": platform_issue['message'] if platform_issue else f"{platform} credentials not configured",
                        "skipped": True
                    }
                    continue
                
                try:
                    task.platform = platform
                    # Use user-specific publisher instead of agent's default publisher
                    success = await user_publisher.publish(
                        content=task.content,
                        platform=platform,
                        content_type=task.type,
                        metadata=task.metadata
                    )
                    if success:
                        success_count += 1
                        results[platform] = {"success": True, "published": True}
                    else:
                        results[platform] = {"success": False, "error": "Publishing failed", "published": False}
                except Exception as e:
                    # Import the custom exceptions
                    from agent.publisher import CredentialsError, PlatformDisabledError, PublishingError
                    
                    if isinstance(e, CredentialsError):
                        error_msg = f"🔑 {e.message}"
                        results[platform] = {
                            "success": False, 
                            "error": error_msg,
                            "error_type": "credentials",
                            "missing_fields": getattr(e, 'missing_fields', []),
                            "published": False
                        }
                    elif isinstance(e, PlatformDisabledError):
                        error_msg = f"⚠️ {e.message}"
                        results[platform] = {
                            "success": False, 
                            "error": error_msg,
                            "error_type": "disabled",
                            "published": False
                        }
                    else:
                        error_msg = f"❌ Publishing failed: {str(e)}"
                        results[platform] = {
                            "success": False, 
                            "error": error_msg,
                            "error_type": "error",
                            "published": False
                        }
            
            overall_success = success_count > 0
            result = {
                "success": overall_success, 
                "published_platforms": success_count,
                "total_platforms": len(platforms),
                "ready_platforms": ready_platforms,
                "credential_issues": credential_check['issues'],
                "platform_results": results
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
        images: List = None,
        current_user: dict = Depends(get_current_user)
    ):
        """Publish content with images to specified platforms."""
        try:
            import tempfile
            import os
            
            # Parse platforms from JSON string
            import json
            platform_list = json.loads(platforms)
            
            user_email = current_user["email"]
            
            # Check credentials for all requested platforms BEFORE publishing
            credential_check = user_settings_manager.check_multiple_platforms(user_email, platform_list)
            
            if not credential_check['can_publish']:
                logger.warning(f"User {user_email} attempted to publish with images without proper credentials")
                return JSONResponse(
                    content={
                        "success": False,
                        "error": "Missing platform credentials",
                        "message": "Please configure your platform credentials before publishing.",
                        "issues": credential_check['issues'],
                        "ready_platforms": credential_check['ready_platforms'],
                        "redirect_to_settings": True
                    },
                    status_code=400
                )
            
            # If there are some issues but some platforms are ready, warn but allow publishing
            if credential_check['issues']:
                logger.warning(f"Some platforms have credential issues for user {user_email}: {credential_check['issues']}")
            
            logger.info(f"Publishing content with images to platforms: {platform_list}")
            logger.info(f"Content length: {len(content)}")
            logger.info(f"Ready platforms: {credential_check['ready_platforms']}")
            
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
            ready_platforms = credential_check['ready_platforms']
            results = {}
            
            # Get user-specific publisher
            user_publisher = agent.get_user_publisher(user_email)
            
            for platform in platform_list:
                if platform not in ready_platforms:
                    # Skip platforms with credential issues
                    platform_issue = next((issue for issue in credential_check['issues'] if issue['platform'] == platform), None)
                    results[platform] = {
                        "success": False, 
                        "error": platform_issue['message'] if platform_issue else f"{platform} credentials not configured",
                        "skipped": True
                    }
                    logger.warning(f"❌ Skipping {platform} - credentials not configured")
                    continue
                
                try:
                    logger.info(f"Publishing to {platform} with {len(image_paths)} images")
                    
                    # Use the enhanced user-specific publisher with image support
                    result = await user_publisher.publish(
                        content=content,
                        platform=platform,
                        content_type=content_type,
                        images=image_paths if image_paths else None
                    )
                    
                    if result:
                        success_count += 1
                        results[platform] = {"success": True, "published": True}
                        logger.info(f"✅ Successfully published to {platform}")
                    else:
                        results[platform] = {"success": False, "error": "Publishing failed", "published": False}
                        logger.error(f"❌ Failed to publish to {platform}")
                        
                except Exception as e:
                    # Import the custom exceptions
                    from agent.publisher import CredentialsError, PlatformDisabledError, PublishingError
                    
                    if isinstance(e, CredentialsError):
                        error_msg = f"🔑 {e.message}"
                        results[platform] = {
                            "success": False, 
                            "error": error_msg,
                            "error_type": "credentials",
                            "missing_fields": getattr(e, 'missing_fields', []),
                            "published": False
                        }
                    elif isinstance(e, PlatformDisabledError):
                        error_msg = f"⚠️ {e.message}"
                        results[platform] = {
                            "success": False, 
                            "error": error_msg,
                            "error_type": "disabled",
                            "published": False
                        }
                    else:
                        error_msg = f"❌ Publishing failed: {str(e)}"
                        results[platform] = {
                            "success": False, 
                            "error": error_msg,
                            "error_type": "error",
                            "published": False
                        }
                    logger.error(f"Error publishing to {platform}: {error_msg}")
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
                "ready_platforms": ready_platforms,
                "platforms": platform_list,
                "images_uploaded": len(image_paths),
                "credential_issues": credential_check['issues'],
                "platform_results": results
            }
            
            logger.info(f"Publishing result: {result}")
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"Error publishing content with images: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/analytics", response_class=HTMLResponse)
    async def analytics_page(request: Request, current_user: dict = Depends(get_current_user)):
        """Analytics dashboard page."""
        try:
            analytics = await agent.get_analytics_report(days=30)
            return templates.TemplateResponse(
                "analytics.html",
                {"request": request, "analytics": analytics, "user": current_user}
            )
        except Exception as e:
            logger.error(f"Error loading analytics: {e}")
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": str(e)}
            )
    
    @app.get("/api/analytics")
    async def get_analytics_api(days: int = 30, current_user: dict = Depends(get_current_user)):
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
    
    # New user settings endpoints
    @app.post("/settings/platform")
    async def save_platform_settings(request: Request, current_user: dict = Depends(get_current_user)):
        """Save platform-specific settings for a user"""
        try:
            data = await request.json()
            platform = data.get('platform')
            enabled = data.get('enabled', False)
            config = data.get('config', {})
            
            user_email = current_user["email"]
            
            settings = {
                'enabled': enabled,
                'config': config
            }
            
            success = user_settings_manager.save_platform_settings(user_email, platform, settings)
            
            if success:
                return JSONResponse(content={"success": True, "message": f"{platform} settings saved successfully"})
            else:
                return JSONResponse(
                    content={"success": False, "detail": "Failed to save settings"},
                    status_code=500
                )
        except Exception as e:
            logger.error(f"Error saving platform settings: {e}")
            return JSONResponse(
                content={"success": False, "detail": str(e)},
                status_code=500
            )
    
    @app.post("/settings/startup")
    async def save_startup_settings(request: Request, current_user: dict = Depends(get_current_user)):
        """Save startup information for a user"""
        try:
            data = await request.json()
            user_email = current_user["email"]
            
            success = user_settings_manager.save_startup_settings(user_email, data)
            
            if success:
                return JSONResponse(content={"success": True, "message": "Startup settings saved successfully"})
            else:
                return JSONResponse(
                    content={"success": False, "detail": "Failed to save startup settings"},
                    status_code=500
                )
        except Exception as e:
            logger.error(f"Error saving startup settings: {e}")
            return JSONResponse(
                content={"success": False, "detail": str(e)},
                status_code=500
            )
    
    @app.post("/settings/test-connection")
    async def test_platform_connection(request: Request, current_user: dict = Depends(get_current_user)):
        """Test connection to a platform with given credentials"""
        try:
            data = await request.json()
            platform = data.get('platform')
            config = data.get('config', {})
            
            result = user_settings_manager.test_platform_connection(platform, config)
            
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"Error testing platform connection: {e}")
            return JSONResponse(
                content={"success": False, "error": str(e)},
                status_code=500
            )
    
    @app.post("/settings/check-credentials")
    async def check_platform_credentials(request: Request, current_user: dict = Depends(get_current_user)):
        """Check if user has configured credentials for specified platforms"""
        try:
            data = await request.json()
            platforms = data.get('platforms', [])
            user_email = current_user["email"]
            
            credential_check = user_settings_manager.check_multiple_platforms(user_email, platforms)
            
            return JSONResponse(content={
                "success": True,
                "credential_status": credential_check
            })
        except Exception as e:
            logger.error(f"Error checking credentials: {e}")
            return JSONResponse(
                content={"success": False, "error": str(e)},
                status_code=500
            )
    
    @app.post("/settings/facebook/validate-token")
    async def validate_facebook_token(request: Request, current_user: dict = Depends(get_current_user)):
        """Validate and auto-renew Facebook token if needed"""
        try:
            user_email = current_user["email"]
            facebook_settings = user_settings_manager.get_platform_settings(user_email, 'facebook')
            
            if not facebook_settings or not facebook_settings.get('enabled'):
                return JSONResponse(
                    content={"success": False, "error": "Facebook not configured or disabled"},
                    status_code=400
                )
            
            # Import Facebook token manager
            try:
                from agent.facebook_token_manager import validate_facebook_credentials, auto_token_manager
                
                facebook_config = facebook_settings.get('config', {})
                result = auto_token_manager.check_and_refresh_token(user_email, facebook_config)
                
                # If token was renewed, save it back
                if result.get('token_renewed') and result.get('new_token'):
                    facebook_config['access_token'] = result['new_token']
                    user_settings_manager.save_platform_settings(
                        user_email, 
                        'facebook', 
                        {'enabled': facebook_settings['enabled'], 'config': facebook_config}
                    )
                    logger.info(f"Updated Facebook token for user {user_email}")
                
                return JSONResponse(content={
                    "success": result['success'],
                    "message": result['message'],
                    "token_renewed": result.get('token_renewed', False),
                    "needs_manual_intervention": result.get('needs_manual_intervention', False)
                })
                
            except ImportError:
                return JSONResponse(
                    content={"success": False, "error": "Facebook token manager not available"},
                    status_code=500
                )
            
        except Exception as e:
            logger.error(f"Error validating Facebook token: {e}")
            return JSONResponse(
                content={"success": False, "error": str(e)},
                status_code=500
            )
    
    @app.post("/settings/facebook/manual-token-update")
    async def manual_facebook_token_update(request: Request, current_user: dict = Depends(get_current_user)):
        """Manually update Facebook token with a new one"""
        try:
            data = await request.json()
            new_token = data.get('access_token', '').strip()
            
            if not new_token:
                return JSONResponse(
                    content={"success": False, "error": "Access token is required"},
                    status_code=400
                )
            
            user_email = current_user["email"]
            facebook_settings = user_settings_manager.get_platform_settings(user_email, 'facebook')
            
            if not facebook_settings:
                return JSONResponse(
                    content={"success": False, "error": "Facebook not configured"},
                    status_code=400
                )
            
            # Test the new token
            try:
                from agent.facebook_token_manager import FacebookTokenManager
                
                facebook_config = facebook_settings.get('config', {})
                app_id = facebook_config.get('app_id')
                app_secret = facebook_config.get('app_secret')
                page_id = facebook_config.get('page_id')
                
                if not all([app_id, app_secret, page_id]):
                    return JSONResponse(
                        content={"success": False, "error": "Missing Facebook app credentials (app_id, app_secret, page_id)"},
                        status_code=400
                    )
                
                token_manager = FacebookTokenManager(app_id, app_secret)
                is_valid, message = token_manager.validate_for_publishing(new_token, page_id)
                
                if not is_valid:
                    return JSONResponse(
                        content={"success": False, "error": f"Token validation failed: {message}"},
                        status_code=400
                    )
                
                # Save the new token
                facebook_config['access_token'] = new_token
                user_settings_manager.save_platform_settings(
                    user_email, 
                    'facebook', 
                    {'enabled': facebook_settings['enabled'], 'config': facebook_config}
                )
                
                return JSONResponse(content={
                    "success": True,
                    "message": f"Facebook token updated successfully. {message}"
                })
                
            except ImportError:
                # Fallback without full validation
                facebook_config = facebook_settings.get('config', {})
                facebook_config['access_token'] = new_token
                user_settings_manager.save_platform_settings(
                    user_email, 
                    'facebook', 
                    {'enabled': facebook_settings['enabled'], 'config': facebook_config}
                )
                
                return JSONResponse(content={
                    "success": True,
                    "message": "Facebook token updated (validation unavailable)"
                })
            
        except Exception as e:
            logger.error(f"Error updating Facebook token: {e}")
            return JSONResponse(
                content={"success": False, "error": str(e)},
                status_code=500
            )
    
    @app.get("/settings/current")
    async def get_current_settings(request: Request, current_user: dict = Depends(get_current_user)):
        """Get current settings for a user"""
        try:
            user_email = current_user["email"]
            settings = user_settings_manager.get_all_user_settings(user_email)
            
            return JSONResponse(content=settings)
        except Exception as e:
            logger.error(f"Error getting current settings: {e}")
            return JSONResponse(
                content={"success": False, "detail": str(e)},
                status_code=500
            )
    
    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page(request: Request, current_user: dict = Depends(get_current_user)):
        """Settings page."""
        try:
            user_email = current_user["email"]
            
            # Get user-specific configuration
            user_config = user_settings_manager.generate_user_config(user_email)
            
            # Get connection status for all platforms
            connection_status = social_auth.get_connection_status()
            configured_platforms = social_auth.get_configured_platforms()
            
            return templates.TemplateResponse(
                "settings.html",
                {
                    "request": request,
                    "config": user_config,
                    "connection_status": connection_status,
                    "configured_platforms": configured_platforms,
                    "user": current_user
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