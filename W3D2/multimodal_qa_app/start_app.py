#!/usr/bin/env python3
"""
Complete startup script for the Multimodal QA Web App.
Starts both backend and frontend servers.
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed: {e}")

def start_frontend():
    """Start the React frontend server."""
    print("🎨 Starting frontend server...")
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    try:
        subprocess.run(["npm", "start"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed: {e}")

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Node.js not found")
            return False
        print(f"✓ Node.js {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js not installed")
        return False
    
    # Check backend dependencies
    backend_dir = Path(__file__).parent / "backend"
    if not (backend_dir / "requirements.txt").exists():
        print("❌ Backend requirements.txt not found")
        return False
    
    # Check frontend dependencies
    frontend_dir = Path(__file__).parent / "frontend"
    if not (frontend_dir / "package.json").exists():
        print("❌ Frontend package.json not found")
        return False
    
    # Check .env file
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found in backend directory")
        print("Please copy .env.example to .env and add your API keys")
        return False
    
    print("✓ All requirements check passed")
    return True

def install_dependencies():
    """Install dependencies for both backend and frontend."""
    print("📦 Installing dependencies...")
    
    # Install backend dependencies
    print("Installing Python dependencies...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Python dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False
    
    # Install frontend dependencies
    print("Installing Node.js dependencies...")
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    try:
        subprocess.run(["npm", "install"], check=True)
        print("✓ Node.js dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Node.js dependencies")
        return False
    
    return True

def main():
    """Main startup function."""
    print("🤖 Multimodal QA Web App - Complete Startup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed")
        
        install_choice = input("\nWould you like to install dependencies? (y/n): ")
        if install_choice.lower() == 'y':
            if not install_dependencies():
                print("❌ Dependency installation failed")
                return
        else:
            print("Please install dependencies manually and try again")
            return
    
    print("\n🎯 Starting application servers...")
    print("Backend will be available at: http://localhost:8000")
    print("Frontend will be available at: http://localhost:3000")
    print("Press Ctrl+C to stop both servers\n")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    try:
        # Start frontend (this will block)
        start_frontend()
    except KeyboardInterrupt:
        print("\n👋 Shutting down application...")

if __name__ == "__main__":
    main()
