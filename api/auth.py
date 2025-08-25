#!/usr/bin/env python3
"""
Authentication routes for Ki Wellness AI Service
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Check if user is admin
            if not user.is_admin:
                return jsonify({'success': False, 'error': 'Access denied. Admin privileges required.'}), 403
            
            login_user(user)
            return jsonify({'success': True, 'redirect': '/'})
        else:
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/check-auth')
def check_auth():
    """Check if user is authenticated and is admin"""
    if current_user.is_authenticated and current_user.is_admin:
        return jsonify({
            'success': True, 
            'user': {
                'username': current_user.username,
                'name': current_user.name,
                'is_admin': current_user.is_admin
            }
        })
    else:
        return jsonify({'success': False, 'authenticated': False}), 401
