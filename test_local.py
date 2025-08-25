#!/usr/bin/env python3
"""
Local test script for Ki Wellness AI Service
Tests imports and basic functionality
"""

import os
import sys

# Add current directory to Python path (same as in app.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔍 Testing Ki Wellness AI Service imports...")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries

try:
    print("\n📦 Testing basic imports...")
    import requests
    print("✅ requests imported successfully")
    
    from flask import Flask
    print("✅ Flask imported successfully")
    
    print("\n🏗️ Testing local module imports...")
    
    # Test models import
    try:
        from models.database import init_db, get_db_connection
        print("✅ models.database imported successfully")
    except ImportError as e:
        print(f"❌ models.database import failed: {e}")
    
    # Test utils import
    try:
        from utils.auth import verify_api_key
        print("✅ utils.auth imported successfully")
    except ImportError as e:
        print(f"❌ utils.auth import failed: {e}")
    
    # Test api imports
    try:
        from api.chat import chat_bp
        print("✅ api.chat imported successfully")
    except ImportError as e:
        print(f"❌ api.chat import failed: {e}")
    
    try:
        from api.health import health_bp
        print("✅ api.health imported successfully")
    except ImportError as e:
        print(f"❌ api.health import failed: {e}")
    
    # Test resources import
    try:
        from resources.health_resources import get_relevant_resources
        print("✅ resources.health_resources imported successfully")
    except ImportError as e:
        print(f"❌ resources.health_resources import failed: {e}")
    
    print("\n🎯 Testing app.py import...")
    try:
        from app import app
        print("✅ app.py imported successfully")
        print("✅ Flask app created successfully")
    except ImportError as e:
        print(f"❌ app.py import failed: {e}")
    except Exception as e:
        print(f"❌ app.py execution failed: {e}")
    
    print("\n✅ All tests completed!")
    
except Exception as e:
    print(f"❌ Test failed with error: {e}")
    import traceback
    traceback.print_exc()
