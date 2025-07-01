#!/usr/bin/env python3
"""
Hapivet Prompt Library - Startup Script
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main startup function"""
    print("🚀 Starting Hapivet Prompt Library...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Warning: .env file not found. Please copy env.example to .env and configure your settings.")
        print("   You can still run the application, but some features may not work without proper configuration.")
    
    # Check if config.yaml exists
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("❌ Error: config.yaml not found. Please ensure the configuration file exists.")
        sys.exit(1)
    
    # Set default environment variables if not set
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Start the server
    print("📡 Starting FastAPI server on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/v1/health")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "src.api.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Hapivet Prompt Library...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 