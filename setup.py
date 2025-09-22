"""
Setup script for UI Regression Agent
"""

import os
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "temp",
        "src/mcp_servers",
        "src/utils",
        "src/engine"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    print("OPENAI_API_KEY: " + os.getenv("OPENAI_API_KEY"))
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables before running the agent:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    print("✅ All required environment variables are set")
    return True


def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import fastapi
        import llama_index
        import streamlit
        import PIL
        import pytest
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def main():
    """Main setup function"""
    print("🔍 Setting up UI Regression Agent...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    print()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    print()
    
    print("🎉 Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Run tests: python -m pytest")
    print("2. Start web interface: streamlit run app.py --server.port 8000")
    print("3. Run CLI demo: python main.py screenshots/login_baseline.png screenshots/login_updated.png")


if __name__ == "__main__":
    main()
