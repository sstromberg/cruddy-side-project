"""
Database models for Employee Directory
Optimized for Aurora Serverless
"""
from . import db
import json
import uuid

class Employee(db.Model):
    """Employee model for Aurora Serverless"""
    __tablename__ = 'employees'
    
    id = db.Column(db.String(36), primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    badges = db.Column(db.Text)
    
    def __init__(self, **kwargs):
        # Generate ID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = f"emp-{str(uuid.uuid4())[:8]}"
        super().__init__(**kwargs)
    
    def to_dict(self):
        """Convert employee to dictionary format"""
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
        return cls(
            id=data.get('id'),
            fullname=data.get('fullname'),
            location=data.get('location'),
            job_title=data.get('job_title'),
            badges=json.dumps(data.get('badges', []))
        )
    
    def __repr__(self):
        return f'<Employee {self.fullname}>'

# Database utility functions
def get_employees():
    """Get all employees"""
    try:
        return [emp.to_dict() for emp in Employee.query.all()]
    except Exception as e:
        print(f"Error getting employees: {e}")
        return []

def get_employee(employee_id):
    """Get employee by ID"""
    try:
        employee = Employee.query.get(employee_id)
        return employee.to_dict() if employee else None
    except Exception as e:
        print(f"Error getting employee {employee_id}: {e}")
        return None

def create_employee(employee_data):
    """Create new employee"""
    try:
        employee = Employee.from_dict(employee_data)
        db.session.add(employee)
        db.session.commit()
        return employee.to_dict()
    except Exception as e:
        print(f"Error creating employee: {e}")
        db.session.rollback()
        return None

def update_employee(employee_id, employee_data):
    """Update existing employee"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return None
        
        for key, value in employee_data.items():
            if key != 'id' and hasattr(employee, key):
                if key == 'badges':
                    setattr(employee, key, json.dumps(value))
                else:
                    setattr(employee, key, value)
        
        db.session.commit()
        return employee.to_dict()
    except Exception as e:
        print(f"Error updating employee {employee_id}: {e}")
        db.session.rollback()
        return None

def delete_employee(employee_id):
    """Delete employee"""
    try:
        employee = Employee.query.get(employee_id)
        if employee:
            db.session.delete(employee)
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error deleting employee {employee_id}: {e}")
        db.session.rollback()
        return False
