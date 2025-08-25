#!/usr/bin/env python3
"""
Test script to demonstrate Ollama download progress monitoring
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_progress_monitor():
    """Test the progress monitor functionality"""
    print("🧪 Testing Ollama Progress Monitor...")
    
    # Check if the progress monitor script exists
    if not os.path.exists("ollama_progress.py"):
        print("❌ ollama_progress.py not found")
        return False
    
    # Check if required dependencies are available
    try:
        import requests
        print("✅ requests module available")
    except ImportError:
        print("❌ requests module not available. Install with: pip install requests")
        return False
    
    print("✅ All dependencies available")
    print("🚀 Progress monitor is ready to use!")
    
    # Show how to use it
    print("\n📖 Usage:")
    print("  python3 ollama_progress.py          # Run full health check and download")
    print("  python3 ollama_progress.py          # Monitor model downloads with progress")
    
    return True

def show_environment_info():
    """Show current environment configuration"""
    print("\n🔧 Environment Configuration:")
    print(f"  OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'mistral')}")
    print(f"  OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
    
    # Check if Ollama is accessible
    try:
        import requests
        response = requests.get(f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/tags", timeout=5)
        if response.status_code == 200:
            print("  Ollama Status: ✅ Running and accessible")
        else:
            print("  Ollama Status: ❌ Not responding")
    except:
        print("  Ollama Status: ❌ Not accessible")

if __name__ == "__main__":
    print("🤖 Ollama Download Progress Test")
    print("=" * 50)
    
    # Test progress monitor
    if test_progress_monitor():
        show_environment_info()
        print("\n🎉 Progress monitor is ready!")
    else:
        print("\n💥 Progress monitor setup failed")
        sys.exit(1)
