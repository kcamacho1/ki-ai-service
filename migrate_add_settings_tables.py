#!/usr/bin/env python3
"""
Migration script to add AI settings and global files tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

def run_migration():
    """Run the migration to create new tables"""
    
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
            
            # Create ai_settings table
            print("📋 Creating ai_settings table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ai_settings (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    model_name VARCHAR(100) DEFAULT 'mistral',
                    temperature FLOAT DEFAULT 0.7,
                    max_tokens INTEGER DEFAULT 2000,
                    system_prompt TEXT DEFAULT 'You are a helpful AI assistant for Ki Wellness.',
                    context_window INTEGER DEFAULT 10,
                    enable_memory BOOLEAN DEFAULT TRUE,
                    response_style VARCHAR(50) DEFAULT 'professional',
                    include_sources BOOLEAN DEFAULT TRUE,
                    max_response_length INTEGER DEFAULT 500,
                    use_global_files BOOLEAN DEFAULT TRUE,
                    file_context_limit INTEGER DEFAULT 5,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_by INTEGER REFERENCES "user"(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create global_files table
            print("📁 Creating global_files table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS global_files (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    file_size INTEGER,
                    content TEXT,
                    content_summary TEXT,
                    is_processed BOOLEAN DEFAULT FALSE,
                    processing_status VARCHAR(50) DEFAULT 'pending',
                    is_active BOOLEAN DEFAULT TRUE,
                    priority INTEGER DEFAULT 1,
                    tags TEXT,
                    category VARCHAR(100),
                    uploaded_by INTEGER REFERENCES "user"(id),
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                )
            """))
            
            # Create chat_sessions table
            print("💬 Creating chat_sessions table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) UNIQUE NOT NULL,
                    user_id INTEGER REFERENCES "user"(id),
                    settings_id INTEGER REFERENCES ai_settings(id),
                    custom_settings TEXT,
                    title VARCHAR(200),
                    message_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes for better performance
            print("⚡ Creating indexes...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ai_settings_active ON ai_settings(is_active)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_global_files_active ON global_files(is_active)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_global_files_priority ON global_files(priority DESC)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_global_files_category ON global_files(category)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_sessions_active ON chat_sessions(is_active)"))
            
            # Insert default AI settings
            print("⚙️ Creating default AI settings...")
            conn.execute(text("""
                INSERT INTO ai_settings (name, description, model_name, temperature, max_tokens, system_prompt, context_window, enable_memory, response_style, include_sources, max_response_length, use_global_files, file_context_limit, is_active)
                VALUES ('Default Settings', 'Default AI settings for Ki Wellness', 'mistral', 0.7, 2000, 'You are a supportive AI Health Coach for Ki Wellness. Keep responses short, helpful, and actionable.', 10, TRUE, 'professional', TRUE, 500, TRUE, 5, TRUE)
                ON CONFLICT (name) DO NOTHING
            """))
            
            # Create API keys table
            print("🔑 Creating API keys table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id SERIAL PRIMARY KEY,
                    key_hash VARCHAR(64) UNIQUE NOT NULL,
                    key_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_by INTEGER REFERENCES "user"(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                )
            """))
            
            # Create indexes for API keys
            print("⚡ Creating API keys indexes...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active)"))
            
            conn.commit()
            print("✅ Migration completed successfully!")
            return True
            
    except ProgrammingError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting AI Settings Migration...")
    success = run_migration()
    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)
