#!/usr/bin/env python3
"""Development server startup script"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import huggingface_hub
        print("✓ Core dependencies installed")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nPlease run: pip install -r requirements_simple.txt")
        sys.exit(1)

def setup_directories():
    """Create necessary directories"""
    dirs = ["models", "uploads", "logs", "data"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✓ Directories created")

def check_env():
    """Check environment variables"""
    if not os.path.exists(".env"):
        print("⚠ No .env file found. Creating from .env.example...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ Created .env file. Please update it with your settings.")
        else:
            print("✗ No .env.example file found!")
            sys.exit(1)
    else:
        print("✓ Environment file found")

def main():
    """Run the development server"""
    print("🚀 Starting DermaMed Development Server\n")
    
    # Check everything is set up
    check_requirements()
    setup_directories()
    check_env()
    
    print("\n📝 Notes:")
    print("- Default credentials: demo_doctor / demo123")
    print("- API docs: http://localhost:8000/docs")
    print("- Health check: http://localhost:8000/health\n")
    
    # Start the server
    cmd = [
        "uvicorn",
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")

if __name__ == "__main__":
    main()