#!/usr/bin/env python3
"""
Local run script for Ki Wellness AI Service
Runs the app locally for testing
"""

import os
import sys

# Add current directory to Python path (same as in app.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for local testing
os.environ.setdefault('AI_SERVICE_DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db')
os.environ.setdefault('AI_SERVICE_SECRET_KEY', 'local-test-secret-key')
os.environ.setdefault('VALID_API_KEYS', 'test-api-key')
os.environ.setdefault('OLLAMA_MODEL', 'mistral')
os.environ.setdefault('FINE_TUNED_MODEL', 'ki-wellness-mistral')
os.environ.setdefault('OLLAMA_BASE_URL', 'http://localhost:11434')
os.environ.setdefault('ALLOWED_ORIGINS', 'http://localhost:5000')

print("🚀 Starting Ki Wellness AI Service locally...")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")

try:
    # Import and run the app
    from app import app
    
    print("✅ App imported successfully!")
    print("🌐 Starting Flask development server...")
    print("📱 Access the app at: http://localhost:5001")
    print("🔑 Use API key: test-api-key")
    print("⏹️  Press Ctrl+C to stop")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False  # Disable reloader to avoid import issues
    )
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("🔍 Run 'python test_local.py' to debug import issues")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Runtime error: {e}")
    import traceback
    traceback.print_exc()
