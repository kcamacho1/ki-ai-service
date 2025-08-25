#!/usr/bin/env python3
"""
Training API endpoints for Ki Wellness AI Service
"""

import os
import json
import time
from datetime import datetime
from flask import Blueprint, request, jsonify
import ollama
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..utils.auth import require_api_key, get_user_from_request, sanitize_input
from ..models.database import log_user_interaction, store_training_example, get_knowledge_base_content

training_bp = Blueprint('training', __name__)

# Configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
FINE_TUNED_MODEL = os.getenv('FINE_TUNED_MODEL', 'ki-wellness-mistral')
TRAINING_FILES_DIR = os.getenv('TRAINING_FILES_DIR', 'training_files')

@training_bp.route('/status', methods=['GET'])
@require_api_key
def training_status():
    """Get training system status"""
    try:
        # Check Ollama models
        try:
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
        except Exception as e:
            available_models = []
            print(f"Error listing models: {e}")
        
        # Check training files
        training_files = []
        if os.path.exists(TRAINING_FILES_DIR):
            for file_path in Path(TRAINING_FILES_DIR).glob('*'):
                if file_path.is_file():
                    training_files.append({
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
        
        return jsonify({
            'success': True,
            'status': {
                'ollama_available': len(available_models) > 0,
                'available_models': available_models,
                'fine_tuned_model_available': FINE_TUNED_MODEL in available_models,
                'training_files_count': len(training_files),
                'training_files': training_files
            }
        })
        
    except Exception as e:
        print(f"Training Status - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/process-files', methods=['POST'])
@require_api_key
def process_training_files():
    """Process training files to extract knowledge"""
    try:
        data = request.get_json() or {}
        files_dir = data.get('files_dir', TRAINING_FILES_DIR)
        
        if not os.path.exists(files_dir):
            return jsonify({'success': False, 'error': f'Training directory not found: {files_dir}'}), 404
        
        # Process files (simplified version)
        processed_files = []
        for file_path in Path(files_dir).glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt', '.md', '.json']:
                try:
                    # Simple text extraction (in production, use proper PDF/text processing)
                    if file_path.suffix.lower() == '.pdf':
                        # For now, just note the file - implement PDF processing later
                        processed_files.append({
                            'file': file_path.name,
                            'status': 'noted_for_processing',
                            'note': 'PDF processing not yet implemented'
                        })
                    else:
                        # Simple text file processing
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Store in knowledge base (simplified)
                        processed_files.append({
                            'file': file_path.name,
                            'status': 'processed',
                            'content_length': len(content)
                        })
                        
                except Exception as e:
                    processed_files.append({
                        'file': file_path.name,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return jsonify({
            'success': True,
            'processed_files': processed_files,
            'total_files': len(processed_files)
        })
        
    except Exception as e:
        print(f"Process Training Files - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/create-example', methods=['POST'])
@require_api_key
def create_training_example():
    """Create a training example for model improvement"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        question = data.get('question')
        answer = data.get('answer')
        
        if not question or not answer:
            return jsonify({'success': False, 'error': 'Question and answer are required'}), 400
        
        # Sanitize inputs
        question = sanitize_input(question)
        answer = sanitize_input(answer, max_length=2000)
        
        # Get additional data
        context = data.get('context')
        source_file = data.get('source_file')
        category = data.get('category', 'general')
        
        # Store training example
        store_training_example(
            question=question,
            answer=answer,
            context=context,
            source_file=source_file,
            category=category
        )
        
        return jsonify({
            'success': True,
            'message': 'Training example created successfully',
            'example': {
                'question': question[:100] + '...' if len(question) > 100 else question,
                'answer': answer[:100] + '...' if len(answer) > 100 else answer,
                'category': category
            }
        })
        
    except Exception as e:
        print(f"Create Training Example - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/fine-tune', methods=['POST'])
@require_api_key
def fine_tune_model():
    """Fine-tune the AI model with training examples"""
    try:
        data = request.get_json() or {}
        
        # Check if fine-tuned model already exists
        try:
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
            
            if FINE_TUNED_MODEL in available_models:
                return jsonify({
                    'success': True,
                    'message': f'Fine-tuned model {FINE_TUNED_MODEL} already exists',
                    'model_name': FINE_TUNED_MODEL
                })
        except Exception as e:
            print(f"Error checking models: {e}")
            return jsonify({'success': False, 'error': 'Unable to check existing models'}), 500
        
        # For now, return a message that fine-tuning is not yet implemented
        # In production, this would:
        # 1. Collect training examples from database
        # 2. Create a Modelfile
        # 3. Run ollama create command
        # 4. Monitor training progress
        
        return jsonify({
            'success': True,
            'message': 'Fine-tuning not yet implemented in this version',
            'note': 'This endpoint will be implemented in future versions to support model fine-tuning'
        })
        
    except Exception as e:
        print(f"Fine-tune Model - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/knowledge-base/search', methods=['POST'])
@require_api_key
def search_knowledge_base():
    """Search the knowledge base for relevant content"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        query = data.get('query')
        if not query:
            return jsonify({'success': False, 'error': 'Search query is required'}), 400
        
        query = sanitize_input(query)
        limit = data.get('limit', 5)
        
        # Search knowledge base
        results = get_knowledge_base_content(query, limit)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_results': len(results)
        })
        
    except Exception as e:
        print(f"Search Knowledge Base - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/performance/feedback', methods=['POST'])
@require_api_key
def submit_performance_feedback():
    """Submit feedback on model performance for improvement"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        question = data.get('question')
        expected_answer = data.get('expected_answer')
        actual_answer = data.get('actual_answer')
        accuracy_score = data.get('accuracy_score')
        feedback = data.get('feedback')
        
        if not question or not actual_answer:
            return jsonify({'success': False, 'error': 'Question and actual answer are required'}), 400
        
        # Sanitize inputs
        question = sanitize_input(question)
        expected_answer = sanitize_input(expected_answer) if expected_answer else None
        actual_answer = sanitize_input(actual_answer)
        feedback = sanitize_input(feedback) if feedback else None
        
        # Store performance feedback (simplified - would use database in production)
        print(f"Performance Feedback - Question: {question[:100]}...")
        print(f"Expected: {expected_answer[:100] if expected_answer else 'None'}...")
        print(f"Actual: {actual_answer[:100]}...")
        print(f"Score: {accuracy_score}")
        print(f"Feedback: {feedback}")
        
        return jsonify({
            'success': True,
            'message': 'Performance feedback submitted successfully',
            'feedback_id': f"fb_{int(time.time())}"
        })
        
    except Exception as e:
        print(f"Submit Performance Feedback - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/models/list', methods=['GET'])
@require_api_key
def list_models():
    """List available Ollama models"""
    try:
        models = ollama.list()
        available_models = []
        
        for model in models['models']:
            model_info = {
                'name': model['name'],
                'size': model.get('size', 0),
                'modified_at': model.get('modified_at', ''),
                'digest': model.get('digest', '')
            }
            available_models.append(model_info)
        
        return jsonify({
            'success': True,
            'models': available_models,
            'total_models': len(available_models)
        })
        
    except Exception as e:
        print(f"List Models - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@training_bp.route('/models/test', methods=['POST'])
@require_api_key
def test_model():
    """Test a specific model with a simple prompt"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        model_name = data.get('model_name', OLLAMA_MODEL)
        test_prompt = data.get('prompt', 'Say "Hello, AI is working!"')
        
        # Test the model
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": test_prompt}]
            )
            
            ai_response = response['message']['content']
            
            return jsonify({
                'success': True,
                'model_name': model_name,
                'test_prompt': test_prompt,
                'response': ai_response,
                'status': 'working'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'model_name': model_name,
                'error': str(e),
                'status': 'error'
            }), 500
        
    except Exception as e:
        print(f"Test Model - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
