#!/usr/bin/env python3
"""
Ki Wellness AI - Simple Chat Interface
A simplified version with basic chat functionality and GUI
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import ollama

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ki-wellness-secret-key')

# Configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2:latest')
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT', 'You are a helpful AI assistant for Ki Wellness, focused on health and wellness topics.')

# Store conversation history (in production, use a database)
conversation_history = []

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        user_tone = data.get('tone', 'friendly')
        custom_instructions = data.get('instructions', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Build the prompt with user preferences
        prompt = _build_prompt(user_message, user_tone, custom_instructions)
        
        # Call Ollama
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            
            ai_response = response['message']['content']
        except Exception as e:
            print(f"Ollama chat error: {e}")
            ai_response = "I'm sorry, but I'm currently unable to process your request. The AI service is temporarily unavailable. Please try again later."
        
        # Store conversation
        conversation_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_message': user_message,
            'ai_response': ai_response,
            'tone': user_tone,
            'instructions': custom_instructions
        }
        conversation_history.append(conversation_entry)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': conversation_entry['timestamp']
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': f'Chat failed: {str(e)}'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    return jsonify({
        'success': True,
        'history': conversation_history
    })

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/api/status', methods=['GET'])
def status():
    """Check service status"""
    try:
        # Test Ollama connection
        models = ollama.list()
        available_models = [model['name'] for model in models['models']]
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'model': OLLAMA_MODEL,
            'model_available': OLLAMA_MODEL in available_models,
            'available_models': available_models,
            'conversation_count': len(conversation_history)
        })
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return jsonify({
            'success': True,
            'status': 'degraded',
            'model': OLLAMA_MODEL,
            'model_available': False,
            'available_models': [],
            'conversation_count': len(conversation_history),
            'warning': 'Ollama not available - chat functionality disabled'
        })

def _build_prompt(user_message, tone, instructions):
    """Build the prompt with user preferences"""
    prompt_parts = []
    
    # Add tone instruction
    if tone and tone != 'default':
        prompt_parts.append(f"Please respond in a {tone} tone.")
    
    # Add custom instructions
    if instructions:
        prompt_parts.append(f"Additional instructions: {instructions}")
    
    # Add user message
    prompt_parts.append(f"User: {user_message}")
    
    return "\n".join(prompt_parts)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting Ki Wellness AI Chat")
    print(f"📱 Model: {OLLAMA_MODEL}")
    print(f"🌐 Port: {port}")
    print(f"🔧 Debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
