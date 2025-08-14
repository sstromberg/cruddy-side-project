import os

# Flask configuration
FLASK_SECRET = os.getenv('FLASK_SECRET', 'dev-secret-key-change-in-production')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///employees.db')

# Environment
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
