#!/usr/bin/env python3
"""
Authentication and authorization utilities for Ki Wellness AI Service
"""

import os
import hashlib
import time
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict, Any
try:
    from models.database import log_api_usage
except ImportError:
    def log_api_usage(api_key_hash, endpoint):
        """Fallback function when database is not available"""
        pass

def verify_api_key(request_obj) -> bool:
    """Verify the API key from the request"""
    api_key = request_obj.headers.get('X-API-Key') or request_obj.args.get('api_key')
    
    if not api_key:
        return False
    
    # Get valid API keys from environment
    valid_keys = os.getenv('VALID_API_KEYS', '').split(',')
    valid_keys = [key.strip() for key in valid_keys if key.strip()]
    
    if not valid_keys:
        # Fallback to a default key for development
        valid_keys = ['ki-wellness-ai-service-key']
    
    # Check if the provided key is valid
    if api_key in valid_keys:
        # Log API usage
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        log_api_usage(api_key_hash, request_obj.endpoint or 'unknown')
        return True
    
    return False

def require_api_key(f):
    """Decorator to require valid API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not verify_api_key(request):
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_by_user(user_id: str, max_requests: int = 100, window_seconds: int = 3600):
    """Simple rate limiting by user ID"""
    # This is a simplified rate limiter
    # In production, use Redis or a more sophisticated solution
    
    current_time = int(time.time())
    window_start = current_time - window_seconds
    
    # For now, just return True (allow all requests)
    # In production, implement proper rate limiting logic
    return True

def get_user_from_request(request_obj) -> Optional[str]:
    """Extract user ID from request headers or parameters"""
    # Check for user ID in headers
    user_id = request_obj.headers.get('X-User-ID')
    if user_id:
        return user_id
    
    # Check for user ID in query parameters
    user_id = request_obj.args.get('user_id')
    if user_id:
        return user_id
    
    # Check for user ID in JSON body
    if request_obj.is_json:
        data = request_obj.get_json()
        user_id = data.get('user_id') if data else None
        if user_id:
            return user_id
    
    return None

def generate_session_id() -> str:
    """Generate a unique session ID for tracking user interactions"""
    import uuid
    return str(uuid.uuid4())

def validate_request_data(required_fields: list, data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate that required fields are present in request data"""
    if not data:
        return False, "No data provided"
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, ""

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def log_security_event(event_type: str, user_id: str = None, details: str = None):
    """Log security-related events"""
    import logging
    
    logger = logging.getLogger('security')
    log_message = f"SECURITY: {event_type}"
    
    if user_id:
        log_message += f" | User: {user_id}"
    
    if details:
        log_message += f" | Details: {details}"
    
    logger.warning(log_message)
