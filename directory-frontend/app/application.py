"""
Demo Flask application - Simplified for direct execution
"""
import os
import json
import uuid
from flask import Flask, render_template, url_for, redirect, flash, g, request
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, validators, PasswordField
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt

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

# Initialize rate limiter
limiter = Limiter(
    app=application,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# User model for authentication
class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='employee')  # admin, manager, employee
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def set_password(self, password):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f'<User {self.username}>'

# Employee model for SQLite
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

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

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

class LoginForm(FlaskForm):
    """Login form for user authentication"""
    username = StringField(
        u'Username',
        [
            validators.InputRequired(message="Username is required"),
            validators.Length(
                min=3,
                max=80,
                message="Username must be between 3 and 80 characters"
            )
        ],
        render_kw={
            "placeholder": "Enter your username",
            "class": "form-control",
            "autocomplete": "username"
        }
    )
    
    password = PasswordField(
        u'Password',
        [
            validators.InputRequired(message="Password is required"),
            validators.Length(
                min=6,
                message="Password must be at least 6 characters"
            )
        ],
        render_kw={
            "placeholder": "Enter your password",
            "class": "form-control",
            "autocomplete": "current-password"
        }
    )

class UserForm(FlaskForm):
    """User registration/management form"""
    username = StringField(
        u'Username',
        [
            validators.InputRequired(message="Username is required"),
            validators.Length(
                min=3,
                max=80,
                message="Username must be between 3 and 80 characters"
            ),
            validators.Regexp(
                r'^[a-zA-Z0-9_-]+$',
                message="Username can only contain letters, numbers, underscores, and hyphens"
            )
        ],
        render_kw={
            "placeholder": "Enter username (e.g., johndoe)",
            "class": "form-control",
            "maxlength": "80"
        }
    )
    
    email = StringField(
        u'Email',
        [
            validators.InputRequired(message="Email is required"),
            validators.Email(message="Please enter a valid email address"),
            validators.Length(
                max=120,
                message="Email cannot exceed 120 characters"
            )
        ],
        render_kw={
            "placeholder": "Enter email address",
            "class": "form-control",
            "type": "email",
            "maxlength": "120"
        }
    )
    
    full_name = StringField(
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
    
    password = PasswordField(
        u'Password',
        [
            validators.InputRequired(message="Password is required"),
            validators.Length(
                min=8,
                message="Password must be at least 8 characters"
            ),
            validators.Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
                message="Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
            )
        ],
        render_kw={
            "placeholder": "Enter password (min 8 chars, mixed case, numbers, symbols)",
            "class": "form-control",
            "autocomplete": "new-password"
        }
    )
    
    role = StringField(
        u'Role',
        [
            validators.InputRequired(message="Role is required"),
            validators.AnyOf(
                ['admin', 'manager', 'employee'],
                message="Role must be admin, manager, or employee"
            )
        ],
        render_kw={
            "class": "form-control"
        }
    )

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
        print("Sample employee data initialized successfully")
    except Exception as e:
        print(f"Error initializing sample employee data: {e}")
        db.session.rollback()

def init_sample_users():
    """Initialize sample user accounts"""
    # Check if admin user already exists
    if User.query.filter_by(username='admin').first():
        print("Admin user already exists")
        return
    
    # Create admin user
    admin_user = User(
        id=f"user-{str(uuid.uuid4())[:8]}",
        username='admin',
        email='admin@company.com',
        full_name='System Administrator',
        role='admin'
    )
    admin_user.set_password('Admin123!')
    
    # Create sample employee user
    employee_user = User(
        id=f"user-{str(uuid.uuid4())[:8]}",
        username='employee',
        email='employee@company.com',
        full_name='Sample Employee',
        role='employee'
    )
    employee_user.set_password('Employee123!')
    
    try:
        db.session.add(admin_user)
        db.session.add(employee_user)
        db.session.commit()
        print("Sample user accounts initialized successfully")
        print("Admin credentials: admin / Admin123!")
        print("Employee credentials: employee / Employee123!")
    except Exception as e:
        print(f"Error initializing sample users: {e}")
        db.session.rollback()

def init_app():
    """Initialize the application"""
    with application.app_context():
        # Initialize SQLAlchemy
        db.init_app(application)
        
        # Create tables and initialize data
        try:
            db.create_all()
            
            # Initialize sample data if tables are empty
            if Employee.query.count() == 0:
                init_sample_data()
            
            if User.query.count() == 0:
                init_sample_users()
                
        except Exception as e:
            print(f"Database initialization error: {e}")

# Initialize the app
init_app()

@application.errorhandler(Exception)
def all_exception_handler(error):
    print(f"Error: {error}")
    return render_template('error.html', error="An error occurred"), 500

@application.route("/")
@login_required
def home():
    "Home screen"
    try:
        employees = [emp.to_dict() for emp in Employee.query.all()]
        return render_template('home.html', employees=employees, badges=badges)
    except Exception as e:
        flash(f'Error loading employees: {str(e)}', 'error')
        return render_template('error.html')

@application.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                if user.is_active:
                    login_user(user, remember=True)
                    next_page = request.args.get('next')
                    if not next_page or not next_page.startswith('/'):
                        next_page = url_for('home')
                    flash(f'Welcome back, {user.full_name}!', 'success')
                    return redirect(next_page)
                else:
                    flash('Account is disabled. Please contact administrator.', 'error')
            else:
                flash('Invalid username or password.', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('login.html', form=form)

@application.route("/logout")
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@application.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per hour")
@login_required
def register():
    """User registration (admin only)"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    form = UserForm()
    if form.validate_on_submit():
        try:
            # Check if username or email already exists
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists.', 'error')
                return render_template('register.html', form=form)
            
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered.', 'error')
                return render_template('register.html', form=form)
            
            # Create new user
            user = User(
                id=f"user-{str(uuid.uuid4())[:8]}",
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'User {user.username} created successfully!', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            flash(f'Error creating user: {str(e)}', 'error')
    
    return render_template('register.html', form=form)

@application.route("/add", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per minute")
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
@login_required
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
@login_required
@limiter.limit("10 per minute")
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
@login_required
@limiter.limit("5 per minute")
def delete(employee_id):
    "Delete employee"
    # Only admins can delete employees
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
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
@login_required
@limiter.limit("100 per hour")
def api_employees():
    """API endpoint to get all employees"""
    try:
        employees = [emp.to_dict() for emp in Employee.query.all()]
        return {'success': True, 'data': employees, 'total': len(employees)}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@application.route('/api/employees/<employee_id>')
@login_required
@limiter.limit("100 per hour")
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
    # Production settings - no debug mode
    application.run(host="0.0.0.0", port=8080, debug=False)
