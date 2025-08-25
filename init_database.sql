-- Ki Wellness AI Service Database Initialization
-- Run this script to create the necessary tables

-- Create tables for API usage tracking
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
);

-- Create tables for user interactions
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
);

-- Create tables for training examples
CREATE TABLE IF NOT EXISTS training_examples (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    example_type VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    quality_score INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tables for knowledge base content
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    content TEXT NOT NULL,
    source VARCHAR(255),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_api_key ON api_usage(api_key_hash);
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_session_id ON user_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_training_examples_user_id ON training_examples(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_content_type ON knowledge_base(content_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_tags ON knowledge_base USING GIN(tags);

-- Insert some initial knowledge base content
INSERT INTO knowledge_base (content_type, title, content, source, tags) VALUES
('nutrition', 'Basic Nutrition Principles', 'A balanced diet includes carbohydrates, proteins, fats, vitamins, and minerals in appropriate proportions.', 'Ki Wellness', ARRAY['nutrition', 'basics']),
('hydration', 'Daily Water Intake', 'Adults should aim for 8-10 glasses of water per day, more if exercising or in hot weather.', 'Ki Wellness', ARRAY['hydration', 'water']),
('exercise', 'Exercise Guidelines', 'Aim for at least 150 minutes of moderate exercise or 75 minutes of vigorous exercise per week.', 'Ki Wellness', ARRAY['exercise', 'fitness']);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for knowledge_base table
CREATE TRIGGER update_knowledge_base_updated_at 
    BEFORE UPDATE ON knowledge_base 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ki_wellness_ai_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ki_wellness_ai_user;
