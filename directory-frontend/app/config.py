"""
Production configuration for Dog Events Tracker
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET', os.urandom(24).hex())
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
    
    # Database Configuration - Default to PostgreSQL to avoid SQLite issues
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/dog_events_db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Configuration
    WTF_CSRF_ENABLED = os.getenv('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = int(os.getenv('WTF_CSRF_TIME_LIMIT', 3600))
    
    # Session Configuration
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.getenv('PERMANENT_SESSION_LIFETIME', 3600)))
    
    # Rate Limiting Configuration
    DEFAULT_RATE_LIMITS = os.getenv('DEFAULT_RATE_LIMITS', '200 per day, 50 per hour')
    LOGIN_RATE_LIMIT = os.getenv('LOGIN_RATE_LIMIT', '5 per minute')
    REGISTER_RATE_LIMIT = os.getenv('REGISTER_RATE_LIMIT', '3 per hour')
    ADD_EDIT_RATE_LIMIT = os.getenv('ADD_EDIT_RATE_LIMIT', '10 per minute')
    DELETE_RATE_LIMIT = os.getenv('DELETE_RATE_LIMIT', '5 per minute')
    API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100 per hour')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/dog_events_tracker.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 10))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Use PostgreSQL for development to avoid SQLite issues
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/dog_events_dev')
    LOG_LEVEL = 'DEBUG'
    
    # Development-specific settings
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/dog_events_prod')
    LOG_LEVEL = 'INFO'
    
    # Production-specific settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # Use in-memory SQLite only for testing
    DATABASE_URL = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    # Testing-specific settings
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
