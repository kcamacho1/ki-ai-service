#!/usr/bin/env python3
"""
Test version of Ki Wellness AI Service without database
Tests imports and basic functionality without requiring a database
"""

import os
import sys

# Add current directory to Python path (same as in app.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for testing
os.environ.setdefault('AI_SERVICE_DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db')
os.environ.setdefault('AI_SERVICE_SECRET_KEY', 'local-test-secret-key')
os.environ.setdefault('VALID_API_KEYS', 'test-api-key')
os.environ.setdefault('OLLAMA_MODEL', 'mistral')
os.environ.setdefault('FINE_TUNED_MODEL', 'ki-wellness-mistral')
os.environ.setdefault('OLLAMA_BASE_URL', 'http://localhost:11434')
os.environ.setdefault('ALLOWED_ORIGINS', 'http://localhost:5000')

print("🔍 Testing Ki Wellness AI Service without database...")

try:
    # Import Flask and basic modules
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    from dotenv import load_dotenv
    import ollama
    from typing import List, Dict, Any, Optional
    
    print("✅ Basic imports successful")
    
    # Import local modules
    from api.chat import chat_bp
    from api.analysis import analysis_bp
    from api.training import training_bp
    from api.health import health_bp
    from utils.auth import verify_api_key, rate_limit_by_user
    from resources.health_resources import get_relevant_resources, format_resources_for_prompt
    
    print("✅ All local module imports successful!")
    
    # Create a minimal app without database
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('AI_SERVICE_SECRET_KEY', 'ai-service-secret-key-change-in-production')
    
    # CORS configuration
    CORS(app, origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000').split(','))
    
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Register blueprints
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(training_bp, url_prefix='/api/training')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    
    @app.route('/')
    def index():
        """Test endpoint"""
        return jsonify({
            'service': 'Ki Wellness AI Service',
            'status': 'imports working!',
            'message': 'All modules imported successfully'
        })
    
    @app.route('/test')
    def test():
        """Test endpoint"""
        return jsonify({
            'success': True,
            'message': 'App is running without database!'
        })
    
    print("✅ Flask app created successfully!")
    print("🌐 Starting test server...")
    print("📱 Access the app at: http://localhost:5001")
    print("⏹️  Press Ctrl+C to stop")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False
    )
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Runtime error: {e}")
    import traceback
    traceback.print_exc()
