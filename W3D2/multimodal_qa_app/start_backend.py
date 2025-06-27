#!/usr/bin/env python3
"""
Startup script for the Multimodal QA backend server.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import openai
        import anthropic
        import PIL
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required keys."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please copy .env.example to .env and add your API keys")
        return False
    
    # Check for at least one API key
    with open(env_file, 'r') as f:
        content = f.read()
        
    has_openai = "OPENAI_API_KEY=" in content and not content.split("OPENAI_API_KEY=")[1].split('\n')[0].strip() == "your_openai_api_key_here"
    has_anthropic = "ANTHROPIC_API_KEY=" in content and not content.split("ANTHROPIC_API_KEY=")[1].split('\n')[0].strip() == "your_anthropic_api_key_here"
    
    if not (has_openai or has_anthropic):
        print("⚠️  No API keys configured in .env file")
        print("Please add at least one API key (OpenAI or Anthropic) to .env")
        return False
    
    print("✓ Environment configuration found")
    return True

def start_server():
    """Start the FastAPI server."""
    print("\n🚀 Starting Multimodal QA Backend Server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main startup function."""
    print("Multimodal QA Backend - Startup Script")
    print("=" * 40)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    checks = [
        ("Checking Python version", check_python_version),
        ("Checking dependencies", check_dependencies),
        ("Checking environment", check_env_file)
    ]
    
    for check_name, check_func in checks:
        print(f"\n{check_name}...")
        if not check_func():
            print(f"\n❌ Startup failed at: {check_name}")
            print("Please resolve the issue and try again.")
            return False
    
    start_server()
    return True

if __name__ == "__main__":
    main()
