#!/usr/bin/env python3
"""
Simple health test for Ki Wellness AI Service
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set minimal environment variables
os.environ.setdefault('AI_SERVICE_DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db')
os.environ.setdefault('AI_SERVICE_SECRET_KEY', 'test-secret-key')
os.environ.setdefault('VALID_API_KEYS', 'test-api-key')

try:
    from app import app
    
    print("✅ App imported successfully")
    
    # Test basic route
    with app.test_client() as client:
        print("Testing /health endpoint...")
        response = client.get('/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        print("\nTesting / endpoint...")
        response = client.get('/')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
