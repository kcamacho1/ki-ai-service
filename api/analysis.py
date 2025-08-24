#!/usr/bin/env python3
"""
Analysis API endpoints for Ki Wellness AI Service
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

analysis_bp = Blueprint('analysis', __name__)

# Configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')

@analysis_bp.route('/generate', methods=['POST'])
@require_api_key
def generate_analysis():
    """Generate AI analysis from user data"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_data = data.get('user_data')
        if not user_data:
            return jsonify({'success': False, 'error': 'User data is required'}), 400
        
        # Get user and session info
        user_id = get_user_from_request(request) or 'anonymous'
        session_id = data.get('session_id') or generate_session_id()
        
        # Prepare comprehensive data for AI analysis
        profile = user_data.get('profile', {})
        food_logs = user_data.get('food_logs', [])
        water_logs = user_data.get('water_logs', [])
        mood_logs = user_data.get('mood_logs', [])
        notes = user_data.get('notes', [])
        
        # Calculate totals and averages
        total_calories = sum(log.get('calories', 0) for log in food_logs)
        avg_calories = total_calories / len(food_logs) if food_logs else 0
        total_water = sum(log.get('amount', 0) for log in water_logs)
        avg_water = total_water / len(water_logs) if water_logs else 0
        avg_mood = sum(log.get('mood', 3) for log in mood_logs) / len(mood_logs) if mood_logs else 3
        
        # Group food by time of day and get top foods
        food_by_time = {}
        for log in food_logs:
            time_of_day = log.get('time_of_day', 'snack')
            if time_of_day not in food_by_time:
                food_by_time[time_of_day] = []
            food_by_time[time_of_day].append(log)
        
        # Get most recent and frequent foods (limit to prevent token overflow)
        recent_foods = food_logs[-3:] if len(food_logs) > 3 else food_logs
        recent_notes = notes[-2:] if len(notes) > 2 else notes
        
        # Build recent activity strings safely
        recent_foods_list = [f"{log.get('name', 'Unknown')} ({log.get('time_of_day', 'snack')})" for log in recent_foods]
        recent_moods_list = [log.get('mood') for log in mood_logs[-2:]]
        recent_notes_list = [
            (note.get('content', '')[:80] + '...') if len(note.get('content', '') or '') > 80 else (note.get('content', '') or '')
            for note in recent_notes
        ]

        analysis_template = (
            """
        Health Coach Analysis - concise, evidence-based, grounded in local knowledge.

        USER: {user_name} | Age: {user_age} | Goals: {user_goals} | Health Concerns: {user_ailments}

        DATA SUMMARY (last 30 days):
        - Food: {food_count} entries, ~{avg_cal:.0f} kcal/day
        - Water: {water_count} entries, ~{avg_water:.1f} cups/day
        - Mood: {mood_count} entries, ~{avg_mood:.1f}/5
        - Notes: {notes_count} entries

        RECENT ACTIVITY:
        - Food (most recent): {recent_foods}
        - Mood (most recent): {recent_moods}
        - Notes (snippets): {recent_notes}

        TASK:
        - Find specific, data-backed patterns connecting mood & notes to food & water intake (e.g., low water -> lower mood next day, high sugar late at night -> poorer mood).
        - Provide short explanations for likely reasons behind how the user is feeling based on these links.
        - Create 2-3 actionable, personalized suggestions to try this week.
        - Ground suggestions in resources the model was trained on (nutrition, hydration, behavior change). Include brief source citations.

        OUTPUT STRICT JSON ONLY:
        {{
          "patterns": [
            {{"title": "Pattern Title", "description": "Brief description of the data-backed link (mood vs. notes, food, water)."}}
          ],
          "suggestions": [
            {{
              "title": "Suggestion Title",
              "description": "Brief, actionable advice tailored to the user's situation.",
              "sources": [
                {{"title": "Short Source Name", "url": "https://example.com"}}
              ]
            }}
          ]
        }}
        """
        )

        analysis_prompt = analysis_template.format(
            user_name=profile.get('name', 'User'),
            user_age=profile.get('age', 'N/A'),
            user_goals=profile.get('health_goals', 'Not specified'),
            user_ailments=profile.get('ailments_concerns', 'Not specified'),
            food_count=len(food_logs),
            avg_cal=avg_calories,
            water_count=len(water_logs),
            avg_water=avg_water,
            mood_count=len(mood_logs),
            avg_mood=avg_mood,
            notes_count=len(notes),
            recent_foods=json.dumps(recent_foods_list),
            recent_moods=json.dumps(recent_moods_list),
            recent_notes=json.dumps(recent_notes_list),
        )
        
        # Call Ollama for analysis
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            ai_response = response['message']['content']
            
            # Parse the JSON response
            try:
                analysis = json.loads(ai_response)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a fallback response
                analysis = {
                    "patterns": [
                        {"title": "Data Analysis", "description": "We're analyzing your wellness patterns. Keep logging to get more personalized insights!"}
                    ],
                    "suggestions": [
                        {"title": "Complete Your Profile", "description": "Add your health goals to your profile to get personalized suggestions."}
                    ]
                }
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log interaction
            log_user_interaction(
                user_id=user_id,
                session_id=session_id,
                interaction_type='analysis_generation',
                request_data={'data_summary': f"{len(food_logs)} food, {len(water_logs)} water, {len(mood_logs)} mood entries"},
                response_data={'analysis': analysis},
                model_used=OLLAMA_MODEL,
                response_time_ms=response_time_ms
            )
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'session_id': session_id,
                'model_used': OLLAMA_MODEL,
                'response_time_ms': response_time_ms
            })
            
        except Exception as ollama_error:
            print(f"AI Analysis - Ollama error: {str(ollama_error)}")
            
            # Provide fallback analysis
            fallback_analysis = {
                "patterns": [
                    {"title": "Getting Started", "description": "Welcome to your AI Health Coach! Start logging your food, water, and mood to get personalized insights."}
                ],
                "suggestions": [
                    {"title": "Complete Your Profile", "description": "Add your health goals to your profile to get personalized suggestions."}
                ]
            }
            
            # Log fallback usage
            response_time_ms = int((time.time() - start_time) * 1000)
            log_user_interaction(
                user_id=user_id,
                session_id=session_id,
                interaction_type='analysis_fallback',
                request_data={'data_summary': f"{len(food_logs)} food, {len(water_logs)} water, {len(mood_logs)} mood entries"},
                response_data={'analysis': fallback_analysis, 'error': str(ollama_error)},
                model_used='fallback',
                response_time_ms=response_time_ms
            )
            
            return jsonify({
                'success': True,
                'analysis': fallback_analysis,
                'session_id': session_id,
                'model_used': 'fallback',
                'note': 'Using fallback analysis - AI model temporarily unavailable',
                'response_time_ms': response_time_ms
            })
        
    except Exception as e:
        print(f"AI Analysis - General error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@analysis_bp.route('/user-summary', methods=['POST'])
@require_api_key
def get_user_summary():
    """Get summarized user data for AI analysis (last 7 days)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_data = data.get('user_data', {})
        user_id = get_user_from_request(request) or 'anonymous'
        
        # Extract data from request
        profile = user_data.get('profile', {})
        food_logs = user_data.get('food_logs', [])
        mood_logs = user_data.get('mood_logs', [])
        water_logs = user_data.get('water_logs', [])
        
        # Create food summary
        food_summary = {
            'total_entries': len(food_logs),
            'avg_calories': sum(log.get('calories', 0) for log in food_logs) / len(food_logs) if food_logs else 0,
            'total_calories': sum(log.get('calories', 0) for log in food_logs),
            'common_foods': _get_common_foods(food_logs),
            'recent_meals': [{
                'name': log.get('name', 'Unknown'),
                'calories': log.get('calories', 0),
                'date': log.get('date', ''),
                'time_of_day': log.get('time_of_day', 'snack')
            } for log in food_logs[-5:]]  # Last 5 meals
        }
        
        # Create mood summary
        mood_summary = {
            'total_entries': len(mood_logs),
            'avg_mood': sum(log.get('mood', 3) for log in mood_logs) / len(mood_logs) if mood_logs else 0,
            'mood_trend': _get_mood_trend(mood_logs),
            'recent_moods': [{
                'mood': log.get('mood', 3),
                'date': log.get('date', '')
            } for log in mood_logs[-5:]]
        }
        
        # Create water summary
        water_summary = {
            'total_entries': len(water_logs),
            'total_water': sum(log.get('amount', 0) for log in water_logs),
            'avg_daily_water': sum(log.get('amount', 0) for log in water_logs) / 7 if water_logs else 0,
            'recent_water': [{
                'amount': log.get('amount', 0),
                'date': log.get('date', '')
            } for log in water_logs[-5:]]
        }
        
        return jsonify({
            'success': True,
            'summary': {
                'profile': profile,
                'food_summary': food_summary,
                'mood_summary': mood_summary,
                'water_summary': water_summary
            }
        })
        
    except Exception as e:
        print(f"User Summary - Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def _get_common_foods(food_logs):
    """Get most common foods from logs"""
    food_counts = {}
    for log in food_logs:
        food_name = log.get('name', 'Unknown')
        food_counts[food_name] = food_counts.get(food_name, 0) + 1
    
    # Sort by frequency and return top 5
    sorted_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)
    return [{'name': food, 'count': count} for food, count in sorted_foods[:5]]

def _get_mood_trend(mood_logs):
    """Calculate mood trend over time"""
    if len(mood_logs) < 2:
        return 'insufficient_data'
    
    # Simple trend calculation
    first_half = mood_logs[:len(mood_logs)//2]
    second_half = mood_logs[len(mood_logs)//2:]
    
    first_avg = sum(log.get('mood', 3) for log in first_half) / len(first_half)
    second_avg = sum(log.get('mood', 3) for log in second_half) / len(second_half)
    
    if second_avg > first_avg + 0.5:
        return 'improving'
    elif second_avg < first_avg - 0.5:
        return 'declining'
    else:
        return 'stable'
