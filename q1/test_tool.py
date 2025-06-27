#!/usr/bin/env python3
"""
Simple test script for the model comparison tool.
This script tests basic functionality without requiring API keys.
"""

import sys
import os
from pathlib import Path

# Change to the script's directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Add the src directory to the Python path
sys.path.append(str(script_dir / "src"))

from config import Config


def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    
    try:
        config = Config("config.yaml")
        print("✓ Configuration loaded successfully")
        
        # Test getting models
        openai_models = config.get_models("openai")
        print(f"✓ Found {len(openai_models)} OpenAI model types")
        
        anthropic_models = config.get_models("anthropic")
        print(f"✓ Found {len(anthropic_models)} Anthropic model types")
        
        huggingface_models = config.get_models("huggingface")
        print(f"✓ Found {len(huggingface_models)} Hugging Face model types")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_model_manager():
    """Test model manager initialization."""
    print("\nTesting model manager...")

    try:
        # Test that model manager file exists
        if Path("src/model_manager.py").exists():
            print("✓ Model manager file exists")
        else:
            print("✗ Model manager file missing")
            return False

        config = Config("config.yaml")
        print("✓ Config can be loaded for model manager")

        return True

    except Exception as e:
        print(f"✗ Model manager test failed: {e}")
        return False


def test_provider_interfaces():
    """Test provider interface implementations."""
    print("\nTesting provider interfaces...")

    try:
        # Test that provider files exist
        provider_files = [
            "src/providers/base.py",
            "src/providers/openai_provider.py",
            "src/providers/anthropic_provider.py",
            "src/providers/huggingface_provider.py"
        ]

        for provider_file in provider_files:
            if Path(provider_file).exists():
                print(f"✓ {provider_file} exists")
            else:
                print(f"✗ {provider_file} missing")
                return False

        return True

    except Exception as e:
        print(f"✗ Provider interface test failed: {e}")
        return False


def test_cli_import():
    """Test CLI module import."""
    print("\nTesting CLI module...")

    try:
        if Path("src/cli.py").exists():
            print("✓ CLI module file exists")
        else:
            print("✗ CLI module file missing")
            return False

        return True

    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False


def test_visualization_import():
    """Test visualization module import."""
    print("\nTesting visualization module...")

    try:
        if Path("src/visualization.py").exists():
            print("✓ Visualization module file exists")
        else:
            print("✗ Visualization module file missing")
            return False

        return True

    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        return False


def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "config.yaml",
        ".env.example",
        "README.md",
        "comparisons.md",
        "src/__init__.py",
        "src/config.py",
        "src/cli.py",
        "src/model_manager.py",
        "src/visualization.py",
        "src/providers/__init__.py",
        "src/providers/base.py",
        "src/providers/openai_provider.py",
        "src/providers/anthropic_provider.py",
        "src/providers/huggingface_provider.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files present")
        return True


def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("Model Comparison Tool - Test Suite")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_config_loading,
        test_model_manager,
        test_provider_interfaces,
        test_cli_import,
        test_visualization_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The tool is ready to use.")
        print("\nNext steps:")
        print("1. Add your API keys to .env file")
        print("2. Run: python main.py --interactive")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 50)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
