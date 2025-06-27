#!/usr/bin/env python3
"""
Setup script for the Model Comparison Tool.
This script helps users set up the environment and dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✓ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\nInstalling dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Set up environment file."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    try:
        # Copy .env.example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        
        print("✓ Created .env file from template")
        print("📝 Please edit .env file and add your API keys")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_plots_directory():
    """Create plots directory for visualizations."""
    plots_dir = Path("plots")
    
    if not plots_dir.exists():
        plots_dir.mkdir()
        print("✓ Created plots directory")
    else:
        print("✓ Plots directory already exists")
    
    return True


def run_tests():
    """Run the test suite."""
    print("\nRunning tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_tool.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False


def show_usage_instructions():
    """Show usage instructions."""
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("1. Edit the .env file and add your API keys:")
    print("   - OPENAI_API_KEY=your_openai_key")
    print("   - ANTHROPIC_API_KEY=your_anthropic_key")
    print("   - HUGGINGFACE_API_KEY=your_huggingface_key")
    
    print("\n2. Run the tool:")
    print("   Interactive mode: python main.py --interactive")
    print("   Single query:    python main.py --query 'Your question here'")
    
    print("\n3. Example commands:")
    print("   python main.py --query 'Explain AI' --model-type instruct")
    print("   python main.py --query 'Write a poem' --provider openai --visualize")
    
    print("\n📚 Documentation:")
    print("   - README.md: Complete usage guide")
    print("   - comparisons.md: Sample outputs and analysis")
    print("   - config.yaml: Model and provider configuration")
    
    print("\n🔧 Troubleshooting:")
    print("   - Run 'python test_tool.py' to verify setup")
    print("   - Check API key validity in the interactive mode")
    print("   - Review logs for detailed error information")
    
    print("=" * 60)


def main():
    """Main setup function."""
    print("Model Comparison Tool - Setup Script")
    print("=" * 40)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_plots_directory),
        ("Running tests", run_tests)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please resolve the issue and run setup again.")
            return False
    
    show_usage_instructions()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
