#!/usr/bin/env python3
"""
Database models and connection management for Ki Wellness AI Service
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

# Global connection pool
connection_pool = None

def init_db(database_url: str):
    """Initialize database tables and connection pool"""
    global connection_pool
    
    try:
        # Create connection pool
        connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            dsn=database_url
        )
        
        # Test connection
        test_conn = connection_pool.getconn()
        connection_pool.putconn(test_conn)
        
        # Create tables
        create_tables()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("⚠️ App will run without database functionality")
        connection_pool = None

def get_db_connection():
    """Get a database connection from the pool"""
    if connection_pool is None:
        raise RuntimeError("Database not available. Check your DATABASE_URL configuration.")
    return connection_pool.getconn()

def return_db_connection(conn):
    """Return a database connection to the pool"""
    if connection_pool:
        connection_pool.putconn(conn)

def create_tables():
    """Create all necessary database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Knowledge base table for storing processed training content
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                source_file TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT UNIQUE NOT NULL,
                embedding TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Training examples table for fine-tuning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_examples (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                context TEXT,
                source_file TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Model performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id SERIAL PRIMARY KEY,
                model_name TEXT NOT NULL,
                question TEXT NOT NULL,
                expected_answer TEXT,
                actual_answer TEXT,
                accuracy_score REAL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User interaction logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT,
                interaction_type TEXT NOT NULL,
                request_data TEXT,
                response_data TEXT,
                model_used TEXT,
                response_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # API usage tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id SERIAL PRIMARY KEY,
                api_key_hash TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                request_count INTEGER DEFAULT 1,
                last_request_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_base_source ON knowledge_base(source_file)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_base_hash ON knowledge_base(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_training_examples_category ON training_examples(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_usage_key ON api_usage(api_key_hash)')
        
        conn.commit()
        print("✅ Database tables created successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        cursor.close()
        return_db_connection(conn)

def log_user_interaction(user_id: str, session_id: str, interaction_type: str, 
                        request_data: Dict, response_data: Dict, model_used: str, 
                        response_time_ms: int):
    """Log user interaction for analytics and improvement"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO user_interactions 
            (user_id, session_id, interaction_type, request_data, response_data, model_used, response_time_ms)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            user_id,
            session_id,
            interaction_type,
            json.dumps(request_data),
            json.dumps(response_data),
            model_used,
            response_time_ms
        ))
        
        conn.commit()
    except Exception as e:
        print(f"❌ Error logging user interaction: {e}")
        conn.rollback()
    finally:
        cursor.close()
        return_db_connection(conn)

def log_api_usage(api_key_hash: str, endpoint: str):
    """Log API usage for rate limiting and analytics"""
    if connection_pool is None:
        print("⚠️ Database not available - skipping API usage logging")
        return
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if usage record exists
        cursor.execute('''
            SELECT id, request_count FROM api_usage 
            WHERE api_key_hash = %s AND endpoint = %s
        ''', (api_key_hash, endpoint))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing record
            cursor.execute('''
                UPDATE api_usage 
                SET request_count = request_count + 1, last_request_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (result[0],))
        else:
            # Create new record
            cursor.execute('''
                INSERT INTO api_usage (api_key_hash, endpoint)
                VALUES (%s, %s)
            ''', (api_key_hash, endpoint))
        
        conn.commit()
    except Exception as e:
        print(f"❌ Error logging API usage: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            return_db_connection(conn)

def get_knowledge_base_content(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get relevant content from knowledge base (simplified search for now)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Simple text search - in production, use vector similarity search
        cursor.execute('''
            SELECT content, metadata, source_file
            FROM knowledge_base 
            WHERE content ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s
        ''', (f'%{query}%', limit))
        
        results = cursor.fetchall()
        return [dict(row) for row in results]
        
    except Exception as e:
        print(f"❌ Error searching knowledge base: {e}")
        return []
    finally:
        cursor.close()
        return_db_connection(conn)

def store_training_example(question: str, answer: str, context: str = None, 
                          source_file: str = None, category: str = None):
    """Store a training example for model improvement"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO training_examples (question, answer, context, source_file, category)
            VALUES (%s, %s, %s, %s, %s)
        ''', (question, answer, context, source_file, category))
        
        conn.commit()
        print(f"✅ Training example stored: {question[:50]}...")
        
    except Exception as e:
        print(f"❌ Error storing training example: {e}")
        conn.rollback()
    finally:
        cursor.close()
        return_db_connection(conn)

def close_db_pool():
    """Close the database connection pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("✅ Database connection pool closed")
