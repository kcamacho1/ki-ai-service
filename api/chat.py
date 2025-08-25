#!/usr/bin/env python3
"""
Chat API endpoints for Ki Wellness AI Service
"""

import os
import json
import time
from datetime import datetime
from flask import Blueprint, request, jsonify
import ollama
from typing import Dict, Any, Optional

from utils.auth import require_api_key, get_user_from_request, generate_session_id, sanitize_input
from models.database import log_user_interaction, get_knowledge_base_content
from resources.health_resources import get_relevant_resources, format_resources_for_prompt

chat_bp = Blueprint('chat', __name__)

# Configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
FINE_TUNED_MODEL = os.getenv('FINE_TUNED_MODEL', 'ki-wellness-mistral')

@chat_bp.route('/message', methods=['POST'])
@require_api_key
def chat_message():
    """Handle AI chat messages"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        message = data.get('message')
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Sanitize input
        message = sanitize_input(message)
        
        # Get user and session info
        user_id = get_user_from_request(request) or 'anonymous'
        session_id = data.get('session_id') or generate_session_id()
        context = data.get('context', {})
        context_type = data.get('context_type', 'minimal')
        chat_history = data.get('chat_history', [])
        
        print(f"AI Chat Request - User: {user_id}, Message: {message[:100]}...")
        
        # Create optimized prompt
        try:
            prompt = _create_optimized_prompt(message, context, context_type, chat_history)
            print(f"AI Chat - Prompt length: {len(prompt)} characters")
        except Exception as prompt_error:
            print(f"AI Chat - Prompt creation error: {str(prompt_error)}")
            return jsonify({'success': False, 'error': f'Prompt creation failed: {str(prompt_error)}'}), 500
        
        # Call Ollama
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            
            ai_response = response['message']['content']
            print(f"AI Chat - Response received, length: {len(ai_response)} characters")
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log interaction
            log_user_interaction(
                user_id=user_id,
                session_id=session_id,
                interaction_type='chat',
                request_data={'message': message, 'context_type': context_type},
                response_data={'response': ai_response},
                model_used=OLLAMA_MODEL,
                response_time_ms=response_time_ms
            )
            
            return jsonify({
                'success': True,
                'response': ai_response,
                'session_id': session_id,
                'model_used': OLLAMA_MODEL,
                'response_time_ms': response_time_ms
            })
            
        except Exception as ollama_error:
            print(f"AI Chat - Ollama error: {str(ollama_error)}")
            
            # Provide fallback response
            fallback_response = _get_fallback_response(message, context_type)
            
            # Log fallback usage
            response_time_ms = int((time.time() - start_time) * 1000)
            log_user_interaction(
                user_id=user_id,
                session_id=session_id,
                interaction_type='chat_fallback',
                request_data={'message': message, 'context_type': context_type},
                response_data={'response': fallback_response, 'error': str(ollama_error)},
                model_used='fallback',
                response_time_ms=response_time_ms
            )
            
            return jsonify({
                'success': True,
                'response': fallback_response,
                'session_id': session_id,
                'model_used': 'fallback',
                'note': 'Using fallback response - AI model temporarily unavailable',
                'response_time_ms': response_time_ms
            })
        
    except Exception as e:
        print(f"AI Chat - General error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/enhanced', methods=['POST'])
@require_api_key
def enhanced_chat():
    """Enhanced AI chat using fine-tuned model and RAG"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        question = data.get('question')
        if not question:
            return jsonify({'success': False, 'error': 'Question is required'}), 400
        
        question = sanitize_input(question)
        user_id = get_user_from_request(request) or 'anonymous'
        session_id = data.get('session_id') or generate_session_id()
        
        # Try fine-tuned model first
        try:
            response = ollama.chat(
                model=FINE_TUNED_MODEL,
                messages=[{"role": "user", "content": question}]
            )
            ai_response = response['message']['content']
            model_used = FINE_TUNED_MODEL
        except:
            # Fallback to base model
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": question}]
            )
            ai_response = response['message']['content']
            model_used = OLLAMA_MODEL
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log interaction
        log_user_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type='enhanced_chat',
            request_data={'question': question},
            response_data={'response': ai_response},
            model_used=model_used,
            response_time_ms=response_time_ms
        )
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'session_id': session_id,
            'model_used': model_used,
            'response_time_ms': response_time_ms
        })
        
    except Exception as e:
        print(f"Enhanced Chat - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def _create_optimized_prompt(message: str, context: Dict[str, Any], context_type: str, chat_history: list) -> str:
    """Create an optimized prompt based on context type"""
    
    # Safely get context values
    try:
        profile = context.get('profile', {}) if context else {}
        profile_name = profile.get('name', 'User') if profile else 'User'
    except Exception as e:
        print(f"Error extracting profile data: {e}")
        profile_name = 'User'
    
    # Start with base prompt
    base_prompt = f"You are a supportive AI Health Coach for {profile_name}. Keep responses short, helpful, and actionable.\n\nQuestion: {message}\n\n"
    
    # Add relevant context
    relevant_context = _extract_relevant_context(message, context, context_type)
    if relevant_context:
        base_prompt += f"Relevant Data: {relevant_context}\n"
    
    # Add relevant resources
    resources = get_relevant_resources(context_type, _determine_topic(message))
    if resources:
        base_prompt += format_resources_for_prompt(resources)
    
    base_prompt += """Provide a short, helpful response (max 2-3 sentences) and include relevant links. Format your response as:

[Your helpful response here]

📚 Helpful Resources:
- [Link 1: Brief description]
- [Link 2: Brief description]

Always include at least one link to our Medium blog (kiwellness.medium.com) when relevant, and cite authoritative health sources like Mayo Clinic, WebMD, or Harvard Health for medical advice."""
    
    # Limit prompt size
    if len(base_prompt) > 1000:
        print(f"Warning: Prompt too large ({len(base_prompt)} chars), truncating...")
        base_prompt = f"""You are a supportive AI Health Coach for {profile_name}. Keep responses short, helpful, and actionable.

Question: {message}

Provide a short, helpful response (max 2-3 sentences) and include relevant links. Format your response as:

[Your helpful response here]

📚 Helpful Resources:
- [Link 1: Brief description]
- [Link 2: Brief description]

Always include at least one link to our Medium blog (kiwellness.medium.com) when relevant, and cite authoritative health sources like Mayo Clinic, WebMD, or Harvard Health for medical advice."""
    
    return base_prompt

def _determine_topic(message: str) -> str:
    """Determine the specific topic of the user's question"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['energy', 'energizing', 'boost', 'power', 'fuel', 'calorie', 'calories', 'weight', 'diet', 'meal', 'eating', 'food']):
        return 'nutrition'
    elif any(word in message_lower for word in ['mood', 'feel', 'emotion', 'happy', 'sad', 'stress', 'anxiety', 'depression']):
        return 'mood'
    elif any(word in message_lower for word in ['water', 'hydrate', 'drink', 'fluid', 'dehydrated']):
        return 'hydration'
    elif any(word in message_lower for word in ['exercise', 'workout', 'fitness', 'activity', 'training']):
        return 'exercise'
    elif any(word in message_lower for word in ['health', 'wellness', 'habit', 'lifestyle', 'goal']):
        return 'wellness'
    
    return 'general'

def _get_fallback_response(message: str, context_type: str) -> str:
    """Provide helpful fallback responses when AI model is unavailable"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['anti-inflammation', 'anti-inflammatory', 'inflammation']):
        return """For anti-inflammatory meals, focus on foods rich in omega-3s, antioxidants, and fiber. Try a salmon salad with leafy greens, berries, and walnuts, or a turmeric-spiced lentil soup with ginger.

📚 Helpful Resources:
- [Anti-Inflammatory Diet Guide](https://kiwellness.medium.com/anti-inflammatory-foods) - Ki Wellness blog
- [Mayo Clinic: Anti-inflammatory diet](https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/anti-inflammatory-diet/art-20457586) - Medical guidance"""
    
    elif any(word in message_lower for word in ['energy', 'energizing', 'boost', 'meal', 'food', 'nutrition']):
        return """For sustained energy, combine complex carbs with protein and healthy fats. Try oatmeal with nuts and berries, or a quinoa bowl with vegetables and lean protein.

📚 Helpful Resources:
- [Energy-Boosting Foods](https://kiwellness.medium.com/energy-foods) - Ki Wellness blog
- [Harvard Health: Foods that fight fatigue](https://www.health.harvard.edu/healthbeat/foods-that-fight-fatigue) - Expert advice"""
    
    elif any(word in message_lower for word in ['water', 'hydrate', 'drink']):
        return """Stay hydrated by drinking water throughout the day. Aim for 8-10 glasses daily, and include hydrating foods like cucumbers, watermelon, and citrus fruits.

📚 Helpful Resources:
- [Hydration Tips](https://kiwellness.medium.com/hydration-guide) - Ki Wellness blog
- [WebMD: How much water should you drink?](https://www.webmd.com/diet/how-much-water-to-drink) - Daily recommendations"""
    
    elif any(word in message_lower for word in ['mood', 'feel', 'stress', 'anxiety', 'wellness']):
        return """Support your mood with regular exercise, adequate sleep, and mood-boosting foods like dark chocolate, fatty fish, and leafy greens. Practice stress management techniques daily.

📚 Helpful Resources:
- [Mood-Boosting Habits](https://kiwellness.medium.com/mood-wellness) - Ki Wellness blog
- [Mayo Clinic: Stress management](https://www.mayoclinic.org/healthy-lifestyle/stress-management) - Expert guidance"""
    
    else:
        return """I'm here to support your wellness journey! For personalized guidance, try logging your meals, water intake, and mood regularly. This helps identify patterns and make informed health decisions.

📚 Helpful Resources:
- [Wellness Tips](https://kiwellness.medium.com/wellness-guide) - Ki Wellness blog
- [Personalized Health Coaching](https://kiwellness.org/human-help) - Book a session with our certified nutritionist"""

def _extract_relevant_context(message: str, context: Dict[str, Any], context_type: str) -> str:
    """Extract only context that's relevant to the user's specific question"""
    message_lower = message.lower()
    relevant_parts = []
    
    try:
        if context_type == 'food' and context.get('food_summary'):
            food_data = context['food_summary']
            
            if any(word in message_lower for word in ['energy', 'energizing', 'boost', 'power']):
                relevant_parts.append(f"Logged {food_data.get('total_entries', 0)} meals")
                if food_data.get('avg_calories', 0) > 0:
                    relevant_parts.append(f"avg {food_data.get('avg_calories', 0):.0f} cal/meal")
                    
            elif any(word in message_lower for word in ['calorie', 'calories', 'weight', 'diet']):
                total_cals = food_data.get('total_calories', 0)
                relevant_parts.append(f"Total calories: {total_cals:.0f}")
                if food_data.get('avg_calories', 0) > 0:
                    relevant_parts.append(f"avg {food_data.get('avg_calories', 0):.0f} cal/meal")
        
        elif context_type == 'mood' and context.get('mood_summary'):
            mood_data = context['mood_summary']
            if any(word in message_lower for word in ['mood', 'feel', 'emotion']):
                relevant_parts.append(f"Average mood: {mood_data.get('avg_mood', 0):.1f}/5")
                relevant_parts.append(f"Logged {mood_data.get('total_entries', 0)} mood entries")
        
        elif context_type == 'water' and context.get('water_summary'):
            water_data = context['water_summary']
            if any(word in message_lower for word in ['water', 'hydrate', 'drink']):
                relevant_parts.append(f"Daily water average: {water_data.get('avg_daily_water', 0):.1f} cups")
                relevant_parts.append(f"Total logged: {water_data.get('total_water', 0):.1f} cups")
    
    except Exception as e:
        print(f"Error extracting relevant context: {e}")
    
    return ' | '.join(relevant_parts) if relevant_parts else ""
