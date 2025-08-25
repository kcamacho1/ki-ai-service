#!/usr/bin/env python3
"""
Database models for AI service settings and global files
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Import the same db instance from user model
from models.user import db

class AISettings(db.Model):
    """Global AI settings that apply to all chat sessions"""
    __tablename__ = 'ai_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # AI Model Settings
    model_name = db.Column(db.String(100), default='mistral')
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=2000)
    
    # Chat Behavior Settings
    system_prompt = db.Column(db.Text, default='You are a helpful AI assistant for Ki Wellness.')
    context_window = db.Column(db.Integer, default=10)  # Number of messages to keep in context
    enable_memory = db.Column(db.Boolean, default=True)
    
    # Response Settings
    response_style = db.Column(db.String(50), default='professional')  # professional, friendly, casual
    include_sources = db.Column(db.Boolean, default=True)
    max_response_length = db.Column(db.Integer, default=500)
    
    # File Integration Settings
    use_global_files = db.Column(db.Boolean, default=True)
    file_context_limit = db.Column(db.Integer, default=5)  # Number of files to include in context
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert settings to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'system_prompt': self.system_prompt,
            'context_window': self.context_window,
            'enable_memory': self.enable_memory,
            'response_style': self.response_style,
            'include_sources': self.include_sources,
            'max_response_length': self.max_response_length,
            'use_global_files': self.use_global_files,
            'file_context_limit': self.file_context_limit,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<AISettings {self.name}>'

class GlobalFile(db.Model):
    """Global files that can be used by the AI for context"""
    __tablename__ = 'global_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, txt, docx, etc.
    file_size = db.Column(db.Integer)  # Size in bytes
    
    # Content and Processing
    content = db.Column(db.Text)  # Extracted text content
    content_summary = db.Column(db.Text)  # Brief summary of content
    is_processed = db.Column(db.Boolean, default=False)
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    
    # Usage Settings
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)  # Higher number = higher priority
    tags = db.Column(db.Text)  # JSON array of tags
    category = db.Column(db.String(100))  # health, nutrition, exercise, etc.
    
    # Metadata
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Convert file to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'content_summary': self.content_summary,
            'is_processed': self.is_processed,
            'processing_status': self.processing_status,
            'is_active': self.is_active,
            'priority': self.priority,
            'tags': json.loads(self.tags) if self.tags else [],
            'category': self.category,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count
        }
    
    def get_tags_list(self):
        """Get tags as a list"""
        return json.loads(self.tags) if self.tags else []
    
    def set_tags(self, tags_list):
        """Set tags from a list"""
        self.tags = json.dumps(tags_list) if tags_list else None
    
    def __repr__(self):
        return f'<GlobalFile {self.original_filename}>'

class ChatSession(db.Model):
    """Individual chat sessions with their settings"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Session Settings (can override global settings)
    settings_id = db.Column(db.Integer, db.ForeignKey('ai_settings.id'))
    custom_settings = db.Column(db.Text)  # JSON string of custom settings
    
    # Session Data
    title = db.Column(db.String(200))
    message_count = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'settings_id': self.settings_id,
            'custom_settings': json.loads(self.custom_settings) if self.custom_settings else None,
            'title': self.title,
            'message_count': self.message_count,
            'total_tokens': self.total_tokens,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'
