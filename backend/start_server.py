#!/usr/bin/env python3
"""
No-reload startup script for the Hirely backend server.
Use this when you want a completely stable server without auto-reload.
"""

import uvicorn
import sys
import os
import signal
from pathlib import Path

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print('\n🛑 Received interrupt signal (Ctrl+C)')
    print('🔄 Shutting down server gracefully...')
    sys.exit(0)

def main():
    """Start the FastAPI server without reload for maximum stability."""
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Add the backend directory to Python path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    try:
        print("🚀 Starting Hirely Backend Server...")
        print("📍 Server will be available at: http://localhost:8000")
        print("📚 API docs available at: http://localhost:8000/docs")
        print("💡 Restart manually after making code changes")
        print("⚠️  Use Ctrl+C to stop the server")
        print("=" * 50)
        
        # Use uvicorn.run WITHOUT reload
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # NO RELOAD - this prevents the loop issue
            log_level="info",
            access_log=True,
            workers=1,
            loop="asyncio"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
