"""
Demo Flask application - Simplified for direct execution
"""
import os
import json
import uuid
from flask import Flask, render_template, url_for, redirect, flash, g, request
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, validators
from flask_sqlalchemy import SQLAlchemy

# Create Flask app
application = Flask(__name__)

# Enable CSRF protection
application.config['WTF_CSRF_ENABLED'] = True
application.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour

# Security headers
application.config['SESSION_COOKIE_SECURE'] = True
application.config['SESSION_COOKIE_HTTPONLY'] = True
application.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
application.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Configuration
application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///employees.db')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', os.urandom(24).hex())

# Initialize SQLAlchemy
db = SQLAlchemy()

# Employee model
class Employee(db.Model):
    """Employee model for SQLite"""
    __tablename__ = 'employees'
    
    id = db.Column(db.String(36), primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    badges = db.Column(db.Text)
    
    def to_dict(self):
        """Convert employee to dictionary format"""
        return {
            'id': self.id,
            'fullname': self.fullname,
            'location': self.location,
            'job_title': self.job_title,
            'badges': json.loads(self.badges) if self.badges else []
        }

# Initialize the app with SQLAlchemy
db.init_app(application)

# Badges definition
badges = {
    "apple" : "Mac User",
    "windows" : "Windows User",
    "linux" : "Linux User",
    "video-camera" : "Digital Content Star",
    "trophy" : "Employee of the Month",
    "camera" : "Photographer",
    "plane" : "Frequent Flier",
    "paperclip" : "Paperclip Afficionado",
    "coffee" : "Coffee Snob",
    "gamepad" : "Gamer",
    "bug" : "Bugfixer",
    "umbrella" : "Seattle Fan",
}

### FlaskForm set up
class EmployeeForm(FlaskForm):
    """flask_wtf form class with enhanced validation"""
    employee_id = HiddenField()
    
    fullname = StringField(
        u'Full Name', 
        [
            validators.InputRequired(message="Full name is required"),
            validators.Length(
                min=2, 
                max=100, 
                message="Full name must be between 2 and 100 characters"
            ),
            validators.Regexp(
                r'^[a-zA-Z\s\-\'\.]+$',
                message="Full name can only contain letters, spaces, hyphens, apostrophes, and periods"
            )
        ],
        render_kw={
            "placeholder": "Enter full name (e.g., John Doe)",
            "class": "form-control",
            "maxlength": "100"
        }
    )
    
    location = StringField(
        u'Location', 
        [
            validators.InputRequired(message="Location is required"),
            validators.Length(
                min=2, 
                max=100, 
                message="Location must be between 2 and 100 characters"
            ),
            validators.Regexp(
                r'^[a-zA-Z0-9\s\-\'\.\,]+$',
                message="Location can only contain letters, numbers, spaces, hyphens, apostrophes, periods, and commas"
            )
        ],
        render_kw={
            "placeholder": "Enter location (e.g., Seattle, WA)",
            "class": "form-control",
            "maxlength": "100"
        }
    )
    
    job_title = StringField(
        u'Job Title', 
        [
            validators.InputRequired(message="Job title is required"),
            validators.Length(
                min=2, 
                max=100, 
                message="Job title must be between 2 and 100 characters"
            ),
            validators.Regexp(
                r'^[a-zA-Z\s\-\'\.\,\&]+$',
                message="Job title can only contain letters, spaces, hyphens, apostrophes, periods, commas, and ampersands"
            )
        ],
        render_kw={
            "placeholder": "Enter job title (e.g., Software Engineer)",
            "class": "form-control",
            "maxlength": "100"
        }
    )
    
    badges = HiddenField(u'Badges')

@application.before_request
def before_request():
    "Set up globals referenced in jinja templates"
    try:
        g.hostname = os.uname().nodename
    except:
        g.hostname = "localhost"
    
    # Configure samesite cookies if we are on SSL
    if request.scheme == "https":
        application.config['SESSION_COOKIE_SAMESITE'] = "None"
        application.config['SESSION_COOKIE_SECURE'] = True

def init_sample_data():
    """Initialize sample employee data"""
    sample_employees = [
        {
            'id': 'emp-001',
            'fullname': 'John Doe',
            'location': 'Seattle, WA',
            'job_title': 'Software Engineer',
            'badges': '["apple", "coffee", "bug"]'
        },
        {
            'id': 'emp-002',
            'fullname': 'Jane Smith',
            'location': 'Austin, TX',
            'job_title': 'Product Manager',
            'badges': '["trophy", "plane", "camera"]'
        }
    ]
    
    for emp_data in sample_employees:
        employee = Employee(**emp_data)
        db.session.add(employee)
    
    try:
        db.session.commit()
        print("Sample data initialized successfully")
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.session.rollback()

def init_app():
    """Initialize the application"""
    with application.app_context():
        # Create tables and initialize data
        try:
            db.create_all()
            # Initialize sample data if table is empty
            if Employee.query.count() == 0:
                init_sample_data()
        except Exception as e:
            print(f"Database initialization error: {e}")

# Initialize the app
init_app()

@application.errorhandler(Exception)
def all_exception_handler(error):
    print(f"Error: {error}")
    return render_template('error.html', error="An error occurred"), 500

@application.route("/")
def home():
    "Home screen"
    try:
        employees = [emp.to_dict() for emp in Employee.query.all()]
        return render_template('home.html', employees=employees, badges=badges)
    except Exception as e:
        flash(f'Error loading employees: {str(e)}', 'error')
        return render_template('error.html')

@application.route("/add", methods=["GET", "POST"])
def add():
    "Add new employee"
    form = EmployeeForm()
    if form.validate_on_submit():
        try:
            employee_data = {
                'id': f"emp-{str(uuid.uuid4())[:8]}",
                'fullname': form.fullname.data,
                'location': form.location.data,
                'job_title': form.job_title.data,
                'badges': form.badges.data
            }
            
            employee = Employee(**employee_data)
            db.session.add(employee)
            db.session.commit()
            
            flash('Employee added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error adding employee: {str(e)}', 'error')
    
    return render_template('add-edit.html', employee=None, title='Add Employee', badges=badges)

@application.route("/view/<employee_id>")
def view(employee_id):
    "View employee details"
    try:
        employee = Employee.query.get(employee_id)
        if employee:
            return render_template('view-edit.html', employee=employee.to_dict(), badges=badges)
        else:
            flash('Employee not found', 'error')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error viewing employee: {str(e)}', 'error')
        return redirect(url_for('home'))

@application.route("/edit/<employee_id>", methods=["GET", "POST"])
def edit(employee_id):
    "Edit existing employee"
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            flash('Employee not found', 'error')
            return redirect(url_for('home'))
        
        form = EmployeeForm()
        if form.validate_on_submit():
            employee.fullname = form.fullname.data
            employee.location = form.location.data
            employee.job_title = form.job_title.data
            employee.badges = form.badges.data
            
            db.session.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('view', employee_id=employee_id))
        
        # Pre-populate form
        form.employee_id.data = employee.id
        form.fullname.data = employee.fullname
        form.location.data = employee.location
        form.job_title.data = employee.job_title
        form.badges.data = employee.badges
        
        return render_template('add-edit.html', employee=employee.to_dict(), title='Edit Employee', badges=badges)
        
    except Exception as e:
        flash(f'Error editing employee: {str(e)}', 'error')
        return redirect(url_for('home'))

@application.route("/delete/<employee_id>", methods=["POST"])
def delete(employee_id):
    "Delete employee"
    try:
        employee = Employee.query.get(employee_id)
        if employee:
            db.session.delete(employee)
            db.session.commit()
            flash('Employee deleted successfully!', 'success')
        else:
            flash('Employee not found', 'error')
    except Exception as e:
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('home'))

# API endpoints
@application.route('/api/employees')
def api_employees():
    """API endpoint to get all employees"""
    try:
        employees = [emp.to_dict() for emp in Employee.query.all()]
        return {'success': True, 'data': employees, 'total': len(employees)}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@application.route('/api/employees/<employee_id>')
def api_employee(employee_id):
    """API endpoint to get specific employee"""
    try:
        employee = Employee.query.get(employee_id)
        if employee:
            return {'success': True, 'data': employee.to_dict()}
        else:
            return {'success': False, 'error': 'Employee not found'}, 404
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080, debug=True)
