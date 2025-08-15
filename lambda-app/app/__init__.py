"""
Flask application factory for Employee Directory
Optimized for AWS Lambda deployment
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///employees.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', os.urandom(24).hex())
    
    # Enable CSRF protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    
    # Security headers
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Create tables and initialize data
    with app.app_context():
        try:
            db.create_all()
            # Initialize sample data if table is empty
            from .models import Employee
            if Employee.query.count() == 0:
                init_sample_data()
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    return app

def init_sample_data():
    """Initialize sample employee data"""
    from .models import Employee
    import uuid
    
    sample_employees = [
        {
            'id': 'emp-001',
            'fullname': 'John Doe',
            'location': 'Seattle, WA',
            'job_title': 'Software Engineer',
            'badges': ['apple', 'coffee', 'bug']
        },
        {
            'id': 'emp-002',
            'fullname': 'Jane Smith',
            'location': 'Austin, TX',
            'job_title': 'Product Manager',
            'badges': ['trophy', 'plane', 'camera']
        }
    ]
    
    for emp_data in sample_employees:
        employee = Employee.from_dict(emp_data)
        db.session.add(employee)
    
    try:
        db.session.commit()
        print("Sample data initialized successfully")
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.session.rollback()
