#!/usr/bin/env python3
"""
Ki Wellness AI Service - Standalone AI Model and Resources API
Provides AI chat, analysis, and training capabilities for the main Ki Wellness app
"""

import os
import sys
import json
import requests
import uuid
from datetime import datetime, date, timedelta
from flask import Flask, request, jsonify, render_template, render_template, redirect

# Try to import optional dependencies with fallbacks
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    print("⚠️ Flask-CORS not available. CORS functionality will be disabled.")
    CORS_AVAILABLE = False

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    print("⚠️ Flask-Limiter not available. Rate limiting will be disabled.")
    LIMITER_AVAILABLE = False

try:
    from flask_login import LoginManager, login_required, current_user
    LOGIN_AVAILABLE = True
except ImportError:
    print("⚠️ Flask-Login not available. Authentication will be disabled.")
    LOGIN_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not available. Environment variables must be set manually.")
    pass

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    print("⚠️ Ollama Python client not available. AI functionality will be disabled.")
    OLLAMA_AVAILABLE = False

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    print("⚠️ PostgreSQL support not available. Database functionality will be limited.")
    POSTGRES_AVAILABLE = False

from typing import List, Dict, Any, Optional

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import local modules
from api.chat import chat_bp
from api.analysis import analysis_bp
from api.training import training_bp
from api.health import health_bp
from api.auth import auth_bp
from api.settings import settings_bp
from models.database import init_db, get_db_connection
from models.user import User, db
from utils.auth import verify_api_key, rate_limit_by_user
from resources.health_resources import get_relevant_resources, format_resources_for_prompt

# Load environment variables
# load_dotenv() # This line is now handled by the try/except block above

# Configure Ollama client
# Note: ollama.set_host() is not available in current version
# The base URL is configured through environment variables

def safe_ollama_chat(model, messages, fallback_response="I'm experiencing technical difficulties. Please try again later."):
    """Safely make Ollama API calls with error handling"""
    if not OLLAMA_AVAILABLE:
        return "AI service is currently unavailable. Ollama Python client is not installed."
    
    try:
        # The ollama client will use the OLLAMA_HOST environment variable if set
        # This should be configured in the environment before the app starts
        response = ollama.chat(model=model, messages=messages)
        return response['message']['content']
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return fallback_response

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('AI_SERVICE_SECRET_KEY', 'ai-service-secret-key-change-in-production')

# Database configuration - use the same database as main app
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Normalize old Heroku-style URLs
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Fallback to SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ki_ai_service.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
try:
    db.init_app(app)
    print("✅ SQLAlchemy initialized successfully")
except Exception as e:
    print(f"⚠️ SQLAlchemy initialization failed: {e}")
    print("⚠️ Database functionality will be limited")

# Initialize Flask-Login
if LOGIN_AVAILABLE:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
else:
    print("Flask-Login not available, authentication will be disabled.")

# CORS configuration
if CORS_AVAILABLE:
    CORS(app, origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000').split(','))
else:
    print("Flask-CORS not available, CORS will be disabled.")

# Rate limiting
if LIMITER_AVAILABLE:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
else:
    print("Flask-Limiter not available, rate limiting will be disabled.")

# API Configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
FINE_TUNED_MODEL = os.getenv('FINE_TUNED_MODEL', 'ki-wellness-mistral')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# Database configuration - use the same database as main app
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Normalize old Heroku-style URLs
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    # Fallback to SQLite for development
    DATABASE_URL = 'sqlite:///ki_ai_service.db'

# Initialize database
try:
    if DATABASE_URL:
        init_db(DATABASE_URL)
    else:
        print("⚠️ No DATABASE_URL provided, running without database functionality")
except Exception as e:
    print(f"⚠️ Database initialization failed: {e}")
    print("⚠️ App will run without database functionality")

# Register blueprints
try:
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(training_bp, url_prefix='/api/training')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    print("✅ All API blueprints registered successfully")
except Exception as e:
    print(f"⚠️ Some API blueprints failed to register: {e}")
    # Register only the ones that are available
    try:
        app.register_blueprint(health_bp, url_prefix='/api/health')
    except:
        pass

@app.before_request
def before_request():
    """Verify API key for API endpoints and authentication for web pages"""
    # Skip verification for auth endpoints, health endpoints, and static files
    if request.endpoint and 'static' not in request.endpoint:
        # Allow auth endpoints without verification
        if 'auth' in request.endpoint:
            return
        
        # Allow health endpoints without API key
        if 'health' in request.endpoint or request.endpoint in ['health']:
            return
        
        # For API endpoints, verify API key first
        if request.path.startswith('/api/'):
            # Allow settings endpoints with API key only
            if request.path.startswith('/api/settings/'):
                if not verify_api_key(request):
                    return jsonify({'error': 'Invalid or missing API key'}), 401
            else:
                if not verify_api_key(request):
                    return jsonify({'error': 'Invalid or missing API key'}), 401

@app.route('/')
def public_index():
    """Serve the public AI Service landing page - no login required"""
    return render_template('index.html')

@app.route('/admin')
def admin_index():
    """Serve the AI Service admin page - requires admin login if available"""
    if LOGIN_AVAILABLE:
        if not current_user.is_authenticated:
            return redirect('/auth/login')
        if not current_user.is_admin:
            return redirect('/auth/logout')
    else:
        # If authentication is not available, show a message
        return jsonify({
            'message': 'Admin interface requires authentication, but Flask-Login is not available.',
            'status': 'authentication_disabled'
        }), 503
    return render_template('index.html')

@app.route('/api-keys')
def api_keys():
    """Serve the API keys management page - requires admin login if available"""
    if LOGIN_AVAILABLE:
        if not current_user.is_authenticated:
            return redirect('/auth/login')
        if not current_user.is_admin:
            return redirect('/auth/logout')
    else:
        # If authentication is not available, show a message
        return jsonify({
            'message': 'API keys management requires authentication, but Flask-Login is not available.',
            'status': 'authentication_disabled'
        }), 503
    return render_template('api_keys.html')

@app.route('/test')
def test():
    """Simple test route to verify the app is running"""
    return jsonify({
        'status': 'success',
        'message': 'Ki Wellness AI Service is running',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencies': {
            'flask_cors': CORS_AVAILABLE,
            'flask_limiter': LIMITER_AVAILABLE,
            'flask_login': LOGIN_AVAILABLE,
            'ollama': OLLAMA_AVAILABLE,
            'postgresql': POSTGRES_AVAILABLE
        }
    })

@app.route('/startup')
def startup_status():
    """Check startup status and any potential issues"""
    try:
        # Check database connection
        db_status = 'unknown'
        if POSTGRES_AVAILABLE:
            try:
                conn = get_db_connection()
                conn.close()
                db_status = 'healthy'
            except Exception as e:
                db_status = f'unhealthy: {str(e)}'
        else:
            db_status = 'unavailable (PostgreSQL not installed)'
        
        # Check Ollama connection
        ollama_status = 'unknown'
        if OLLAMA_AVAILABLE:
            try:
                response = safe_ollama_chat(OLLAMA_MODEL, [{"role": "user", "content": "Test"}])
                if response == "AI service is currently unavailable. Ollama Python client is not installed.":
                    ollama_status = 'unhealthy: connection failed'
                else:
                    ollama_status = 'healthy'
            except Exception as e:
                ollama_status = f'unhealthy: {str(e)}'
        else:
            ollama_status = 'unavailable (Ollama Python client not installed)'
        
        return jsonify({
            'service': 'Ki Wellness AI Service',
            'startup_status': 'complete',
            'components': {
                'database': db_status,
                'ollama': ollama_status,
                'flask_app': 'app.py (main application)',
                'environment': os.getenv('FLASK_ENV', 'development')
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'service': 'Ki Wellness AI Service',
            'startup_status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/health')
def health():
    """Service health check"""
    return jsonify({
        'service': 'Ki Wellness AI Service',
        'version': '1.0.0',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Service is running'
    })

@app.route('/api/status')
def status():
    """Detailed service status"""
    try:
        # Check Ollama connection
        ollama_status = 'healthy'
        if OLLAMA_AVAILABLE:
            try:
                response = safe_ollama_chat(OLLAMA_MODEL, [{"role": "user", "content": "Hello"}])
                if response == "AI service is currently unavailable. Ollama Python client is not installed.":
                    ollama_status = 'unhealthy: connection failed'
            except Exception as e:
                ollama_status = f'unhealthy: {str(e)}'
        else:
            ollama_status = 'unavailable (Ollama Python client not installed)'
        
        # Check database connection
        db_status = 'healthy'
        if POSTGRES_AVAILABLE:
            try:
                conn = get_db_connection()
                conn.close()
            except Exception as e:
                db_status = f'unhealthy: {str(e)}'
        else:
            db_status = 'unavailable (PostgreSQL not installed)'
        
        return jsonify({
            'service': 'Ki Wellness AI Service',
            'status': 'healthy' if 'unhealthy' not in ollama_status and 'unhealthy' not in db_status else 'degraded',
            'components': {
                'ollama': ollama_status,
                'database': db_status
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'service': 'Ki Wellness AI Service',
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/ollama-status')
def ollama_status():
    """Detailed Ollama status endpoint"""
    try:
        # Test Ollama connection
        test_response = safe_ollama_chat(OLLAMA_MODEL, [{"role": "user", "content": "Test"}])
        
        if test_response == "AI service is currently unavailable. Ollama Python client is not installed.":
            return jsonify({
                'status': 'unhealthy',
                'error': 'Ollama connection failed',
                'model': OLLAMA_MODEL,
                'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            }), 500
        
        return jsonify({
            'status': 'healthy',
            'model': OLLAMA_MODEL,
            'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            'test_response': test_response[:100] + '...' if len(test_response) > 100 else test_response
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'model': OLLAMA_MODEL,
            'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle any unhandled exceptions"""
    return jsonify({
        'error': 'An unexpected error occurred',
        'message': str(e) if app.debug else 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('AI_SERVICE_PORT', 5001))
    debug = os.getenv('AI_SERVICE_DEBUG', 'false').lower() == 'true'
    
    print("🚀 Starting Ki Wellness AI Service...")
    print(f"📱 Port: {port}")
    print(f"🔧 Debug: {debug}")
    print(f"🌐 Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
