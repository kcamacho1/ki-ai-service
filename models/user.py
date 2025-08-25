#!/usr/bin/env python3
"""
User model for authentication - uses existing Ki Wellness database
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'  # Use existing table name
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    health_goals = db.Column(db.Text)
    ailments_concerns = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Agreement tracking
    agreed_to_terms = db.Column(db.Boolean, default=False)
    agreed_to_privacy = db.Column(db.Boolean, default=False)
    agreed_to_disclaimer = db.Column(db.Boolean, default=False)
    agreements_date = db.Column(db.DateTime)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
