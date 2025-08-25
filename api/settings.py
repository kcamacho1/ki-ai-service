#!/usr/bin/env python3
"""
API endpoints for managing AI settings and global files
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models.settings import AISettings, GlobalFile, ChatSession, db
from datetime import datetime
import os
import json
import uuid
from werkzeug.utils import secure_filename

settings_bp = Blueprint('settings', __name__)

# File upload configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'md', 'json', 'csv'}
UPLOAD_FOLDER = 'static/uploads/global_files'

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path, file_type):
    """Extract text content from uploaded file"""
    try:
        if file_type == 'txt' or file_type == 'md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_type == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        elif file_type == 'csv':
            import csv
            content = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    content.append(', '.join(row))
            return '\n'.join(content)
        else:
            # For PDF and DOCX, return a placeholder
            return f"[Content from {file_type.upper()} file - processing required]"
    except Exception as e:
        return f"Error extracting content: {str(e)}"

# ============================================================================
# AI SETTINGS ENDPOINTS
# ============================================================================

@settings_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    """Get all AI settings"""
    try:
        settings = AISettings.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'settings': [setting.to_dict() for setting in settings]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/<int:setting_id>', methods=['GET'])
@login_required
def get_setting(setting_id):
    """Get specific AI setting"""
    try:
        setting = AISettings.query.get_or_404(setting_id)
        return jsonify({
            'success': True,
            'setting': setting.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings', methods=['POST'])
def create_setting():
    """Create new AI setting"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        # Check if name already exists
        existing = AISettings.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'success': False, 'error': 'Setting with this name already exists'}), 400
        
        # Create new setting
        setting = AISettings(
            name=data['name'],
            description=data.get('description', ''),
            model_name=data.get('model_name', 'mistral'),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', 2000),
            system_prompt=data.get('system_prompt', 'You are a helpful AI assistant for Ki Wellness.'),
            context_window=data.get('context_window', 10),
            enable_memory=data.get('enable_memory', True),
            response_style=data.get('response_style', 'professional'),
            include_sources=data.get('include_sources', True),
            max_response_length=data.get('max_response_length', 500),
            use_global_files=data.get('use_global_files', True),
            file_context_limit=data.get('file_context_limit', 5),
            created_by=current_user.id if current_user.is_authenticated else None
        )
        
        db.session.add(setting)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'setting': setting.to_dict(),
            'message': 'Setting created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/<int:setting_id>', methods=['PUT'])
@login_required
def update_setting(setting_id):
    """Update AI setting"""
    try:
        setting = AISettings.query.get_or_404(setting_id)
        data = request.get_json()
        
        # Update fields
        for field in ['name', 'description', 'model_name', 'temperature', 'max_tokens',
                     'system_prompt', 'context_window', 'enable_memory', 'response_style',
                     'include_sources', 'max_response_length', 'use_global_files', 'file_context_limit']:
            if field in data:
                setattr(setting, field, data[field])
        
        setting.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'setting': setting.to_dict(),
            'message': 'Setting updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/<int:setting_id>', methods=['DELETE'])
@login_required
def delete_setting(setting_id):
    """Delete AI setting"""
    try:
        setting = AISettings.query.get_or_404(setting_id)
        setting.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Setting deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# GLOBAL FILES ENDPOINTS
# ============================================================================

@settings_bp.route('/files', methods=['GET'])
@login_required
def get_files():
    """Get all global files"""
    try:
        files = GlobalFile.query.filter_by(is_active=True).order_by(GlobalFile.priority.desc(), GlobalFile.uploaded_at.desc()).all()
        return jsonify({
            'success': True,
            'files': [file.to_dict() for file in files]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/files/<int:file_id>', methods=['GET'])
@login_required
def get_file(file_id):
    """Get specific global file"""
    try:
        file_obj = GlobalFile.query.get_or_404(file_id)
        return jsonify({
            'success': True,
            'file': file_obj.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/files', methods=['POST'])
def upload_file():
    """Upload new global file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Extract content
        content = extract_text_from_file(file_path, file_extension)
        content_summary = content[:200] + "..." if len(content) > 200 else content
        
        # Create file record
        file_obj = GlobalFile(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_type=file_extension,
            file_size=file_size,
            content=content,
            content_summary=content_summary,
            is_processed=True,
            processing_status='completed',
            priority=request.form.get('priority', 1),
            category=request.form.get('category', 'general'),
            tags=request.form.get('tags', '[]'),
            uploaded_by=current_user.id if current_user.is_authenticated else None
        )
        
        db.session.add(file_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'file': file_obj.to_dict(),
            'message': 'File uploaded successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/files/<int:file_id>', methods=['PUT'])
@login_required
def update_file(file_id):
    """Update global file metadata"""
    try:
        file_obj = GlobalFile.query.get_or_404(file_id)
        data = request.get_json()
        
        # Update fields
        for field in ['priority', 'category', 'is_active']:
            if field in data:
                setattr(file_obj, field, data[field])
        
        # Update tags
        if 'tags' in data:
            file_obj.set_tags(data['tags'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'file': file_obj.to_dict(),
            'message': 'File updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/files/<int:file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    """Delete global file"""
    try:
        file_obj = GlobalFile.query.get_or_404(file_id)
        
        # Delete physical file
        if os.path.exists(file_obj.file_path):
            os.remove(file_obj.file_path)
        
        # Delete database record
        db.session.delete(file_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# CHAT SESSIONS ENDPOINTS
# ============================================================================

@settings_bp.route('/sessions', methods=['GET'])
@login_required
def get_sessions():
    """Get user's chat sessions"""
    try:
        if current_user.is_authenticated:
            sessions = ChatSession.query.filter_by(user_id=current_user.id, is_active=True).order_by(ChatSession.last_activity.desc()).all()
        else:
            sessions = []
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/sessions', methods=['POST'])
@login_required
def create_session():
    """Create new chat session"""
    try:
        data = request.get_json()
        
        session = ChatSession(
            session_id=str(uuid.uuid4()),
            user_id=current_user.id if current_user.is_authenticated else None,
            settings_id=data.get('settings_id'),
            custom_settings=json.dumps(data.get('custom_settings')) if data.get('custom_settings') else None,
            title=data.get('title', 'New Chat')
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'message': 'Session created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@login_required
def update_session(session_id):
    """Update chat session"""
    try:
        if current_user.is_authenticated:
            session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
        else:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        data = request.get_json()
        
        # Update fields
        for field in ['title', 'message_count', 'total_tokens']:
            if field in data:
                setattr(session, field, data[field])
        
        session.last_activity = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'message': 'Session updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@settings_bp.route('/active-settings', methods=['GET'])
def get_active_settings():
    """Get the currently active AI settings"""
    try:
        # Get the first active setting, or create a default one
        setting = AISettings.query.filter_by(is_active=True).first()
        
        if not setting:
            # Create default setting
            setting = AISettings(
                name='Default Settings',
                description='Default AI settings for Ki Wellness',
                created_by=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(setting)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'settings': setting.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/file-categories', methods=['GET'])
def get_file_categories():
    """Get available file categories"""
    try:
        categories = db.session.query(GlobalFile.category).distinct().filter(
            GlobalFile.category.isnot(None),
            GlobalFile.category != ''
        ).all()
        
        return jsonify({
            'success': True,
            'categories': [cat[0] for cat in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
