"""
Database abstraction layer supporting both SQLite (local) and PostgreSQL (production)
"""
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///employees.db')
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'

# Initialize SQLAlchemy
db = SQLAlchemy()
Base = declarative_base()

class Employee(db.Model):
    """Employee model for both local and production databases"""
    __tablename__ = 'employees'
    
    id = db.Column(db.String(36), primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    badges = db.Column(db.Text)  # JSON string for badges
    
    def to_dict(self):
        """Convert employee to dictionary format"""
        import json
        return {
            'id': self.id,
            'fullname': self.fullname,
            'location': self.location,
            'job_title': self.job_title,
            'badges': json.loads(self.badges) if self.badges else []
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create employee from dictionary"""
        import json
        return cls(
            id=data.get('id'),
            fullname=data.get('fullname'),
            location=data.get('location'),
            job_title=data.get('job_title'),
            badges=json.dumps(data.get('badges', []))
        )

def init_database(app):
    """Initialize database with app context"""
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add sample data if table is empty
        if Employee.query.count() == 0:
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
            
            db.session.commit()

def get_employees():
    """Get all employees"""
    return [emp.to_dict() for emp in Employee.query.all()]

def get_employee(employee_id):
    """Get employee by ID"""
    employee = Employee.query.get(employee_id)
    return employee.to_dict() if employee else None

def create_employee(employee_data):
    """Create new employee"""
    import uuid
    if not employee_data.get('id'):
        employee_data['id'] = f"emp-{str(uuid.uuid4())[:8]}"
    
    employee = Employee.from_dict(employee_data)
    db.session.add(employee)
    db.session.commit()
    return employee.to_dict()

def update_employee(employee_id, employee_data):
    """Update existing employee"""
    employee = Employee.query.get(employee_id)
    if not employee:
        return None
    
    for key, value in employee_data.items():
        if key != 'id' and hasattr(employee, key):
            if key == 'badges':
                import json
                setattr(employee, key, json.dumps(value))
            else:
                setattr(employee, key, value)
    
    db.session.commit()
    return employee.to_dict()

def delete_employee(employee_id):
    """Delete employee"""
    employee = Employee.query.get(employee_id)
    if employee:
        db.session.delete(employee)
        db.session.commit()
        return True
    return False
