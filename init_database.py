#!/usr/bin/env python3
"""
Database initialization script for Ki Wellness AI Service
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv

def init_database():
    """Initialize the database with required tables"""
    
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    # Normalize old Heroku-style URLs
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔗 Connected to database successfully")
            
            # Create api_usage table
            print("📊 Creating api_usage table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id SERIAL PRIMARY KEY,
                    api_key_hash VARCHAR(64) NOT NULL,
                    endpoint VARCHAR(255) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id VARCHAR(255),
                    session_id VARCHAR(255),
                    response_time_ms INTEGER,
                    model_used VARCHAR(100),
                    request_data JSONB,
                    response_data JSONB
                )
            """))
            
            # Create user_interactions table
            print("👤 Creating user_interactions table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_id VARCHAR(255) NOT NULL,
                    interaction_type VARCHAR(50) NOT NULL,
                    request_data JSONB,
                    response_data JSONB,
                    model_used VARCHAR(100),
                    response_time_ms INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create training_examples table
            print("🎯 Creating training_examples table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS training_examples (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255),
                    session_id VARCHAR(255),
                    example_type VARCHAR(50) NOT NULL,
                    input_data JSONB NOT NULL,
                    output_data JSONB NOT NULL,
                    quality_score INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create knowledge_base table
            print("📚 Creating knowledge_base table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id SERIAL PRIMARY KEY,
                    content_type VARCHAR(50) NOT NULL,
                    title VARCHAR(255),
                    content TEXT NOT NULL,
                    source VARCHAR(255),
                    tags TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Commit the table creation
            conn.commit()
            
            # Create indexes for better performance
            print("⚡ Creating indexes...")
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_api_usage_api_key ON api_usage(api_key_hash)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_interactions_session_id ON user_interactions(session_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_training_examples_user_id ON training_examples(user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_knowledge_base_content_type ON knowledge_base(content_type)"))
                print("✅ Indexes created successfully")
            except Exception as e:
                print(f"⚠️ Some indexes may already exist: {e}")
            
            # Insert some initial knowledge base content
            print("📝 Inserting initial knowledge base content...")
            try:
                conn.execute(text("""
                    INSERT INTO knowledge_base (content_type, title, content, source, tags) VALUES
                    ('nutrition', 'Basic Nutrition Principles', 'A balanced diet includes carbohydrates, proteins, fats, vitamins, and minerals in appropriate proportions.', 'Ki Wellness', ARRAY['nutrition', 'basics']),
                    ('hydration', 'Daily Water Intake', 'Adults should aim for 8-10 glasses of water per day, more if exercising or in hot weather.', 'Ki Wellness', ARRAY['hydration', 'water']),
                    ('exercise', 'Exercise Guidelines', 'Aim for at least 150 minutes of moderate exercise or 75 minutes of vigorous exercise per week.', 'Ki Wellness', ARRAY['exercise', 'fitness'])
                    ON CONFLICT DO NOTHING
                """))
                print("✅ Knowledge base content inserted successfully")
            except Exception as e:
                print(f"⚠️ Knowledge base content may already exist: {e}")
            
            # Commit all changes
            conn.commit()
            
            print("✅ Database initialization completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_database()
