"""
Demo Flask application - Dog Events Tracker
"""
import os
import json
import uuid
from datetime import datetime, timezone
from flask import Flask, render_template, url_for, redirect, flash, g, request
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, validators, PasswordField, SelectField, DateTimeField
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
import logging
from logging.handlers import RotatingFileHandler
from config import config

# Create Flask app
application = Flask(__name__)

# Load configuration based on environment
config_name = os.getenv('FLASK_ENV', 'default')
application.config.from_object(config[config_name])

# Configure logging for production
if not application.debug:
    # Production logging configuration
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        application.config['LOG_FILE'], 
        maxBytes=application.config['LOG_MAX_SIZE'], 
        backupCount=application.config['LOG_BACKUP_COUNT']
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(getattr(logging, application.config['LOG_LEVEL']))
    application.logger.addHandler(file_handler)
    
    # Console handler for production
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, application.config['LOG_LEVEL']))
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    application.logger.addHandler(console_handler)
    
    application.logger.setLevel(getattr(logging, application.config['LOG_LEVEL']))
    application.logger.info('Dog Events Tracker startup')

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize rate limiter with configurable limits
limiter = Limiter(
    app=application,
    key_func=get_remote_address,
    default_limits=application.config['DEFAULT_RATE_LIMITS'].split(','),
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

# Dog model for SQLite
class Dog(db.Model):
    """Dog model for SQLite"""
    __tablename__ = 'dogs'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    approx_age = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(20), nullable=False)  # Small, Medium, Large
    breed_type = db.Column(db.String(100), nullable=False)
    
    # Relationship to events
    events = db.relationship('Event', backref='dog', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert dog to dictionary format"""
        return {
            'id': self.id,
            'name': self.name,
            'approx_age': self.approx_age,
            'size': self.size,
            'breed_type': self.breed_type
        }

# Event model for SQLite
class Event(db.Model):
    """Event model for SQLite"""
    __tablename__ = 'events'
    
    id = db.Column(db.String(36), primary_key=True)
    dog_id = db.Column(db.String(36), db.ForeignKey('dogs.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # walk, poop, pee, vomit, nap
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    end_timestamp = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(200), nullable=True)  # Optional location
    notes = db.Column(db.Text, nullable=True)  # Optional notes
    bristol_stool_scale = db.Column(db.Integer, nullable=True)  # 1-7 for poop events
    
    def to_dict(self):
        """Convert event to dictionary format"""
        duration = None
        if self.end_timestamp and self.timestamp:
            duration = (self.end_timestamp - self.timestamp).total_seconds() / 60  # in minutes
        
        return {
            'id': self.id,
            'dog_id': self.dog_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'end_timestamp': self.end_timestamp.isoformat() if self.end_timestamp else None,
            'duration': duration,
            'location': self.location,
            'notes': self.notes,
            'bristol_stool_scale': self.bristol_stool_scale
        }

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Event types definition
event_types = {
    "walk": "Walk",
    "poop": "Poop",
    "pee": "Pee", 
    "vomit": "Vomit",
    "nap": "Nap"
}

# Dog sizes definition
dog_sizes = {
    "small": "Small",
    "medium": "Medium", 
    "large": "Large"
}

### FlaskForm set up
class DogForm(FlaskForm):
    """flask_wtf form class for dogs with enhanced validation"""
    dog_id = HiddenField()
    
    name = StringField(
        u'Dog Name', 
        [
            validators.InputRequired(message="Dog name is required"),
            validators.Length(
                min=2, 
                max=100, 
                message="Dog name must be between 2 and 100 characters"
            ),
            validators.Regexp(
                r'^[a-zA-Z\s\-\'\.]+$',
                message="Dog name can only contain letters, spaces, hyphens, apostrophes, and periods"
            )
        ],
        render_kw={
            "placeholder": "Enter dog name (e.g., Max)",
            "class": "form-control",
            "maxlength": "100"
        }
    )
    
    approx_age = StringField(
        u'Approximate Age', 
        [
            validators.InputRequired(message="Approximate age is required"),
            validators.Length(
                min=2, 
                max=50, 
                message="Age must be between 2 and 50 characters"
            ),
            validators.Regexp(
                r'^[a-zA-Z0-9\s\-\'\.]+$',
                message="Age can only contain letters, numbers, spaces, hyphens, apostrophes, and periods"
            )
        ],
        render_kw={
            "placeholder": "Enter approximate age (e.g., 3 years, 6 months)",
            "class": "form-control",
            "maxlength": "50"
        }
    )
    
    size = SelectField(
        u'Size',
        [
            validators.InputRequired(message="Size is required")
        ],
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
        render_kw={
            "class": "form-control"
        }
    )
    
    breed_type = StringField(
        u'Breed/Type', 
        [
            validators.InputRequired(message="Breed/Type is required"),
            validators.Length(
                min=2, 
                max=100, 
                message="Breed/Type must be between 2 and 100 characters"
            ),
            validators.Regexp(
                r'^[a-zA-Z\s\-\'\.\,\&]+$',
                message="Breed/Type can only contain letters, spaces, hyphens, apostrophes, periods, commas, and ampersands"
            )
        ],
        render_kw={
            "placeholder": "Enter breed or type (e.g., Golden Retriever, Mixed)",
            "class": "form-control",
            "maxlength": "100"
        }
    )

class EventForm(FlaskForm):
    """flask_wtf form class for events with enhanced validation"""
    event_id = HiddenField()
    
    dog_id = SelectField(
        u'Dog',
        [
            validators.InputRequired(message="Dog is required")
        ],
        coerce=str,
        render_kw={
            "class": "form-control"
        }
    )
    
    event_type = SelectField(
        u'Event Type',
        [
            validators.InputRequired(message="Event type is required")
        ],
        choices=[('walk', 'Walk'), ('poop', 'Poop'), ('pee', 'Pee'), ('vomit', 'Vomit'), ('nap', 'Nap')],
        render_kw={
            "class": "form-control"
        }
    )
    
    timestamp = DateTimeField(
        u'Start Time',
        [
            validators.InputRequired(message="Start time is required")
        ],
        format='%Y-%m-%dT%H:%M',
        render_kw={
            "class": "form-control",
            "type": "datetime-local"
        }
    )
    
    end_timestamp = DateTimeField(
        u'End Time (Optional)',
        format='%Y-%m-%dT%H:%M',
        render_kw={
            "class": "form-control",
            "type": "datetime-local"
        }
    )
    
    location = StringField(
        u'Location (Optional)',
        [
            validators.Length(
                max=200,
                message="Location cannot exceed 200 characters"
            )
        ],
        render_kw={
            "placeholder": "Enter location (e.g., Backyard, Park, Vet)",
            "class": "form-control",
            "maxlength": "200"
        }
    )
    
    notes = StringField(
        u'Notes (Optional)',
        [
            validators.Length(
                max=1000,
                message="Notes cannot exceed 1000 characters"
            )
        ],
        render_kw={
            "placeholder": "Enter any additional notes about this event",
            "class": "form-control",
            "maxlength": "1000"
        }
    )
    
    bristol_stool_scale = SelectField(
        u'Bristol Stool Scale (Poop events only)',
        [
            validators.Optional()
        ],
        choices=[
            ('', 'Not applicable'),
            ('1', '1 - Separate hard lumps (constipation)'),
            ('2', '2 - Sausage-like but lumpy'),
            ('3', '3 - Sausage-like with cracks'),
            ('4', '4 - Sausage-like, smooth and soft'),
            ('5', '5 - Soft blobs with clear-cut edges'),
            ('6', '6 - Mushy consistency, ragged edges'),
            ('7', '7 - Entirely liquid (diarrhea)')
        ],
        render_kw={
            "class": "form-control"
        }
    )

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
    """Initialize sample dog data"""
    sample_dogs = [
        {
            'id': 'dog-001',
            'name': 'Max',
            'approx_age': '3 years',
            'size': 'medium',
            'breed_type': 'Golden Retriever'
        },
        {
            'id': 'dog-002',
            'name': 'Bella',
            'approx_age': '1 year',
            'size': 'small',
            'breed_type': 'Chihuahua'
        }
    ]
    
    for dog_data in sample_dogs:
        dog = Dog(**dog_data)
        db.session.add(dog)
    
    try:
        db.session.commit()
        application.logger.info("Sample dog data initialized successfully")
    except Exception as e:
        application.logger.error(f"Error initializing sample dog data: {e}")
        db.session.rollback()

def init_sample_events():
    """Initialize sample event data"""
    sample_events = [
        {
            'id': 'evt-001',
            'dog_id': 'dog-001',
            'event_type': 'walk',
            'timestamp': datetime(2024, 1, 15, 8, 0),
            'end_timestamp': datetime(2024, 1, 15, 8, 30),
            'location': 'Neighborhood Park',
            'notes': 'Good energy, met other dogs',
            'bristol_stool_scale': None
        },
        {
            'id': 'evt-002',
            'dog_id': 'dog-001',
            'event_type': 'poop',
            'timestamp': datetime(2024, 1, 15, 8, 15),
            'end_timestamp': None,
            'location': 'Backyard',
            'notes': 'Normal consistency',
            'bristol_stool_scale': 4
        },
        {
            'id': 'evt-003',
            'dog_id': 'dog-002',
            'event_type': 'nap',
            'timestamp': datetime(2024, 1, 15, 10, 0),
            'end_timestamp': datetime(2024, 1, 15, 11, 30),
            'location': 'Living Room',
            'notes': 'Slept soundly on favorite blanket',
            'bristol_stool_scale': None
        }
    ]
    
    for event_data in sample_events:
        event = Event(**event_data)
        db.session.add(event)
    
    try:
        db.session.commit()
        application.logger.info("Sample event data initialized successfully")
    except Exception as e:
        application.logger.error(f"Error initializing sample event data: {e}")
        db.session.rollback()

def init_sample_users():
    """Initialize sample user accounts"""
    # Check if admin user already exists
    if User.query.filter_by(username='admin').first():
        application.logger.info("Admin user already exists")
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
        application.logger.info("Sample user accounts initialized successfully")
        application.logger.info("Admin credentials: admin / Admin123!")
        application.logger.info("Employee credentials: employee / Employee123!")
    except Exception as e:
        application.logger.error(f"Error initializing sample users: {e}")
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
            if Dog.query.count() == 0:
                init_sample_data()
            
            if Event.query.count() == 0:
                init_sample_events()
            
            if User.query.count() == 0:
                init_sample_users()
                
        except Exception as e:
            application.logger.error(f"Database initialization error: {e}")

# Initialize the app
init_app()

@application.errorhandler(Exception)
def all_exception_handler(error):
    application.logger.error(f"Error: {error}")
    return render_template('error.html', error="An error occurred"), 500

@application.route("/")
@login_required
def home():
    "Home screen - list of dogs"
    try:
        dogs = [dog.to_dict() for dog in Dog.query.all()]
        return render_template('home.html', dogs=dogs, dog_sizes=dog_sizes)
    except Exception as e:
        flash(f'Error loading dogs: {str(e)}', 'error')
        return render_template('error.html')

@application.route("/login", methods=["GET", "POST"])
@limiter.limit(application.config['LOGIN_RATE_LIMIT'])
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
@limiter.limit(application.config['REGISTER_RATE_LIMIT'])
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
@limiter.limit(application.config['ADD_EDIT_RATE_LIMIT'])
def add():
    "Add new dog"
    form = DogForm()
    if form.validate_on_submit():
        try:
            dog_data = {
                'id': f"dog-{str(uuid.uuid4())[:8]}",
                'name': form.name.data,
                'approx_age': form.approx_age.data,
                'size': form.size.data,
                'breed_type': form.breed_type.data
            }
            
            dog = Dog(**dog_data)
            db.session.add(dog)
            db.session.commit()
            
            flash('Dog added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error adding dog: {str(e)}', 'error')
    
    return render_template('add-edit.html', dog=None, title='Add Dog', dog_sizes=dog_sizes)

@application.route("/view/<dog_id>")
@login_required
def view(dog_id):
    "View dog details and events"
    try:
        dog = Dog.query.get(dog_id)
        if dog:
            # Get recent events for this dog, ordered by timestamp descending
            events = Event.query.filter_by(dog_id=dog_id).order_by(Event.timestamp.desc()).limit(50).all()
            events_data = [event.to_dict() for event in events]
            return render_template('view-edit.html', dog=dog.to_dict(), events=events_data, event_types=event_types, dog_sizes=dog_sizes)
        else:
            flash('Dog not found', 'error')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error viewing dog: {str(e)}', 'error')
        return redirect(url_for('home'))

@application.route("/edit/<dog_id>", methods=["GET", "POST"])
@login_required
@limiter.limit(application.config['ADD_EDIT_RATE_LIMIT'])
def edit(dog_id):
    "Edit existing dog"
    try:
        dog = Dog.query.get(dog_id)
        if not dog:
            flash('Dog not found', 'error')
            return redirect(url_for('home'))
        
        form = DogForm()
        if form.validate_on_submit():
            dog.name = form.name.data
            dog.approx_age = form.approx_age.data
            dog.size = form.size.data
            dog.breed_type = form.breed_type.data
            
            db.session.commit()
            flash('Dog updated successfully!', 'success')
            return redirect(url_for('view', dog_id=dog_id))
        
        # Pre-populate form
        form.dog_id.data = dog.id
        form.name.data = dog.name
        form.approx_age.data = dog.approx_age
        form.size.data = dog.size
        form.breed_type.data = dog.breed_type
        
        return render_template('add-edit.html', dog=dog.to_dict(), title='Edit Dog', dog_sizes=dog_sizes)
        
    except Exception as e:
        flash(f'Error editing dog: {str(e)}', 'error')
        return redirect(url_for('home'))

@application.route("/delete/<dog_id>", methods=["POST"])
@login_required
@limiter.limit(application.config['DELETE_RATE_LIMIT'])
def delete(dog_id):
    "Delete dog"
    # Only admins can delete dogs
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        dog = Dog.query.get(dog_id)
        if dog:
            db.session.delete(dog)
            db.session.commit()
            flash('Dog deleted successfully!', 'success')
        else:
            flash('Dog not found', 'error')
    except Exception as e:
        flash(f'Error deleting dog: {str(e)}', 'error')
    
    return redirect(url_for('home'))

# Event management routes
@application.route("/add-event", methods=["GET", "POST"])
@login_required
@limiter.limit(application.config['ADD_EDIT_RATE_LIMIT'])
def add_event():
    "Add new event"
    form = EventForm()
    # Populate dog choices
    form.dog_id.choices = [(dog.id, dog.name) for dog in Dog.query.all()]
    
    if form.validate_on_submit():
        try:
            event_data = {
                'id': f"evt-{str(uuid.uuid4())[:8]}",
                'dog_id': form.dog_id.data,
                'event_type': form.event_type.data,
                'timestamp': form.timestamp.data,
                'end_timestamp': form.end_timestamp.data if form.end_timestamp.data else None,
                'location': form.location.data if form.location.data else None,
                'notes': form.notes.data if form.notes.data else None,
                'bristol_stool_scale': int(form.bristol_stool_scale.data) if form.bristol_stool_scale.data and form.bristol_stool_scale.data.isdigit() else None
            }
            
            event = Event(**event_data)
            db.session.add(event)
            db.session.commit()
            
            flash('Event added successfully!', 'success')
            return redirect(url_for('view', dog_id=form.dog_id.data))
        except Exception as e:
            flash(f'Error adding event: {str(e)}', 'error')
    
    return render_template('add-edit-event.html', event=None, title='Add Event', event_types=event_types, dogs=Dog.query.all())

@application.route("/edit-event/<event_id>", methods=["GET", "POST"])
@login_required
@limiter.limit(application.config['ADD_EDIT_RATE_LIMIT'])
def edit_event(event_id):
    "Edit existing event"
    try:
        event = Event.query.get(event_id)
        if not event:
            flash('Event not found', 'error')
            return redirect(url_for('home'))
        
        form = EventForm()
        # Populate dog choices
        form.dog_id.choices = [(dog.id, dog.name) for dog in Dog.query.all()]
        
        if form.validate_on_submit():
            event.dog_id = form.dog_id.data
            event.event_type = form.event_type.data
            event.timestamp = form.timestamp.data
            event.end_timestamp = form.end_timestamp.data if form.end_timestamp.data else None
            event.location = form.location.data if form.location.data else None
            event.notes = form.notes.data if form.notes.data else None
            event.bristol_stool_scale = int(form.bristol_stool_scale.data) if form.bristol_stool_scale.data and form.bristol_stool_scale.data.isdigit() else None
            
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('view', dog_id=event.dog_id))
        
        # Pre-populate form
        form.event_id.data = event.id
        form.dog_id.data = event.dog_id
        form.event_type.data = event.event_type
        form.timestamp.data = event.timestamp
        form.end_timestamp.data = event.end_timestamp
        form.location.data = event.location
        form.notes.data = event.notes
        form.bristol_stool_scale.data = str(event.bristol_stool_scale) if event.bristol_stool_scale else ''
        
        return render_template('add-edit-event.html', event=event.to_dict(), title='Edit Event', event_types=event_types, dogs=Dog.query.all())
        
    except Exception as e:
        flash(f'Error editing event: {str(e)}', 'error')
        return redirect(url_for('home'))

@application.route("/delete-event/<event_id>", methods=["POST"])
@login_required
@limiter.limit(application.config['DELETE_RATE_LIMIT'])
def delete_event(event_id):
    "Delete event"
    # Only admins can delete events
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        event = Event.query.get(event_id)
        if event:
            dog_id = event.dog_id
            db.session.delete(event)
            db.session.commit()
            flash('Event deleted successfully!', 'success')
            return redirect(url_for('view', dog_id=dog_id))
        else:
            flash('Event not found', 'error')
    except Exception as e:
        flash(f'Error deleting event: {str(e)}', 'error')
    
    return redirect(url_for('home'))

# Health check endpoint for production monitoring
@application.route("/health")
def health_check():
    """Health check endpoint for production monitoring"""
    try:
        # Check database connectivity
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        application.logger.error(f"Database health check failed: {e}")
        db_status = 'unhealthy'
    
    # Check application status
    app_status = 'healthy' if application else 'unhealthy'
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' and app_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0',
        'checks': {
            'database': db_status,
            'application': app_status
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return health_data, status_code

# API endpoints
@application.route('/api/dogs')
@login_required
@limiter.limit(application.config['API_RATE_LIMIT'])
def api_dogs():
    """API endpoint to get all dogs"""
    try:
        dogs = [dog.to_dict() for dog in Dog.query.all()]
        return {'success': True, 'data': dogs, 'total': len(dogs)}
    except Exception as e:
        application.logger.error(f"API error in api_dogs: {e}")
        return {'success': False, 'error': str(e)}, 500

@application.route('/api/dogs/<dog_id>')
@login_required
@limiter.limit(application.config['API_RATE_LIMIT'])
def api_dog(dog_id):
    """API endpoint to get specific dog"""
    try:
        dog = Dog.query.get(dog_id)
        if dog:
            return {'success': True, 'data': dog.to_dict()}
        else:
            return {'success': False, 'error': 'Dog not found'}, 404
    except Exception as e:
        application.logger.error(f"API error in api_dog: {e}")
        return {'success': False, 'error': str(e)}, 500

@application.route('/api/dogs/<dog_id>/events')
@login_required
@limiter.limit(application.config['API_RATE_LIMIT'])
def api_dog_events(dog_id):
    """API endpoint to get events for a specific dog"""
    try:
        events = Event.query.filter_by(dog_id=dog_id).order_by(Event.timestamp.desc()).all()
        events_data = [event.to_dict() for event in events]
        return {'success': True, 'data': events_data, 'total': len(events_data)}
    except Exception as e:
        application.logger.error(f"API error in api_dog_events: {e}")
        return {'success': False, 'error': str(e)}, 500

if __name__ == "__main__":
    # Production settings - no debug mode
    application.run(host="0.0.0.0", port=8080, debug=False)
