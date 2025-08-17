#!/usr/bin/env python3
"""
Simple startup script for deployment platforms
"""
import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Railway injects this)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on port {port}")
    
    # Start uvicorn server
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False,
        log_level="info"
    )
