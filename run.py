#!/usr/bin/env python3
"""
Founder Socials AI Agent - Startup Script

Simple script to run the application with default settings.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Simple main function to start the application"""
    try:
        # Try to import and run the main application
        try:
            import uvicorn
            from ui.dashboard import create_dashboard_app
            from agent.core import FounderSocialsAgent
            
            print("🚀 Starting Founder Socials AI Agent...")
            print("📝 Web Dashboard: http://localhost:8000")
            print("� Initializing agent...")
            
            # Create agent
            agent = FounderSocialsAgent()
            
            # Create web app
            app = create_dashboard_app(agent)
            
            print("✅ Agent initialized successfully!")
            print("🌐 Starting web server...")
            
            # Run the web server
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=8000,
                log_level="info"
            )
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("💡 Try installing missing dependencies:")
            print("   pip install fastapi uvicorn")
            return False
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        return True
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 