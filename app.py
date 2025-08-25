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
from flask import Flask, request, jsonify, render_template, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import ollama
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import local modules
from api.chat import chat_bp
from api.analysis import analysis_bp
from api.training import training_bp
from api.health import health_bp
from models.database import init_db, get_db_connection
from utils.auth import verify_api_key, rate_limit_by_user
from resources.health_resources import get_relevant_resources, format_resources_for_prompt

# Load environment variables
load_dotenv()

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

# API Configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
FINE_TUNED_MODEL = os.getenv('FINE_TUNED_MODEL', 'ki-wellness-mistral')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# Database configuration
DATABASE_URL = os.getenv('AI_SERVICE_DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("AI_SERVICE_DATABASE_URL environment variable is required")

# Initialize database
init_db(DATABASE_URL)

# Register blueprints
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(training_bp, url_prefix='/api/training')
app.register_blueprint(health_bp, url_prefix='/api/health')

@app.before_request
def before_request():
    """Verify API key for all requests except health checks"""
    # Skip API key verification for health endpoints and static files
    if request.endpoint and 'static' not in request.endpoint:
        # Allow health endpoints without API key
        if 'health' in request.endpoint or request.endpoint in ['health', 'index']:
            return
        
        if not verify_api_key(request):
            return jsonify({'error': 'Invalid or missing API key'}), 401

@app.route('/')
def index():
    """Serve the AI Service landing page"""
    return render_template('index.html')

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
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": "Hello"}]
            )
        except Exception as e:
            ollama_status = f'unhealthy: {str(e)}'
        
        # Check database connection
        db_status = 'healthy'
        try:
            conn = get_db_connection()
            conn.close()
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        return jsonify({
            'service': 'Ki Wellness AI Service',
            'status': 'healthy',
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('AI_SERVICE_PORT', 5001))
    debug = os.getenv('AI_SERVICE_DEBUG', 'false').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
