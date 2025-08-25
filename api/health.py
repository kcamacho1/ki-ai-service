#!/usr/bin/env python3
"""
Health API endpoints for Ki Wellness AI Service
"""

import os
import time
from datetime import datetime
from flask import Blueprint, jsonify
import ollama
from typing import Dict, Any

from models.database import get_db_connection

health_bp = Blueprint('health', __name__)

@health_bp.route('/check', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'service': 'Ki Wellness AI Service',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@health_bp.route('/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check with component status"""
    start_time = time.time()
    
    health_status = {
        'service': 'Ki Wellness AI Service',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'components': {},
        'response_time_ms': 0
    }
    
    # Check Ollama connection
    try:
        response = ollama.chat(
            model=os.getenv('OLLAMA_MODEL', 'mistral'),
            messages=[{"role": "user", "content": "Hello"}]
        )
        health_status['components']['ollama'] = {
            'status': 'healthy',
            'response_time': 'normal',
            'model': os.getenv('OLLAMA_MODEL', 'mistral')
        }
    except Exception as e:
        health_status['components']['ollama'] = {
            'status': 'unhealthy',
            'error': str(e),
            'model': os.getenv('OLLAMA_MODEL', 'mistral')
        }
        health_status['status'] = 'degraded'
    
    # Check database connection
    try:
        conn = get_db_connection()
        conn.close()
        health_status['components']['database'] = {
            'status': 'healthy',
            'connection': 'established'
        }
    except Exception as e:
        health_status['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'degraded'
    
    # Check environment variables
    required_env_vars = [
        'AI_SERVICE_DATABASE_URL',
        'AI_SERVICE_SECRET_KEY',
        'OLLAMA_MODEL'
    ]
    
    env_status = {}
    for var in required_env_vars:
        if os.getenv(var):
            env_status[var] = 'set'
        else:
            env_status[var] = 'missing'
            health_status['status'] = 'degraded'
    
    health_status['components']['environment'] = env_status
    
    # Calculate response time
    health_status['response_time_ms'] = int((time.time() - start_time) * 1000)
    
    # Determine overall status
    if health_status['status'] == 'degraded':
        if health_status['components']['ollama']['status'] == 'unhealthy' and health_status['components']['database']['status'] == 'unhealthy':
            health_status['status'] = 'unhealthy'
    
    return jsonify(health_status)

@health_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get service metrics"""
    try:
        # Get basic metrics
        metrics = {
            'service': 'Ki Wellness AI Service',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime': 'running',  # In production, calculate actual uptime
            'memory_usage': 'monitored',  # In production, get actual memory usage
            'cpu_usage': 'monitored',  # In production, get actual CPU usage
            'active_connections': 'tracked'  # In production, get actual connection count
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({
            'service': 'Ki Wellness AI Service',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check for Kubernetes/load balancer health checks"""
    try:
        # Check if service is ready to handle requests
        ready = True
        issues = []
        
        # Check Ollama
        try:
            ollama.chat(
                model=os.getenv('OLLAMA_MODEL', 'mistral'),
                messages=[{"role": "user", "content": "Hello"}]
            )
        except Exception as e:
            ready = False
            issues.append(f"Ollama: {str(e)}")
        
        # Check database
        try:
            conn = get_db_connection()
            conn.close()
        except Exception as e:
            ready = False
            issues.append(f"Database: {str(e)}")
        
        if ready:
            return jsonify({
                'status': 'ready',
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'status': 'not_ready',
                'issues': issues,
                'timestamp': datetime.utcnow().isoformat()
            }), 503
            
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """Liveness check for Kubernetes health checks"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    })
