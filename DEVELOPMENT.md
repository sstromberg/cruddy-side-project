# Development Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 13+ (recommended) or Docker
- Virtual environment
- Code editor (VS Code, PyCharm, etc.)
- Git for version control

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd containerized_apps_aws/directory-frontend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Setup PostgreSQL database (recommended)
./setup-dev-db.sh

# Or manually setup PostgreSQL and configure .env
cp env.example .env
# Edit .env with your PostgreSQL connection details

# Install dependencies
pip install -r requirements.txt

# Start development server
python3 run-dev.py
```

## 🏗️ Architecture Overview

### Technology Stack
- **Backend**: Flask 3.1.1 with SQLAlchemy 2.0.23
- **Database**: PostgreSQL (dev & production) - SQLite only for testing
- **Frontend**: Bootstrap 5 with responsive design
- **Authentication**: Flask-Login with bcrypt
- **Security**: CSRF protection, rate limiting, secure headers

### Application Structure
```
app/
├── application.py      # Main Flask app, routes, models
├── database.py         # Database models and operations
├── config.py           # Configuration management
├── templates/          # HTML templates
└── static/             # CSS, JS, images
```

## 🗄️ Database Models

### Dog Model
```python
class Dog(db.Model):
    __tablename__ = 'dogs'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    approx_age = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(20), nullable=False)  # Small, Medium, Large
    breed_type = db.Column(db.String(100), nullable=False)
    
    # Relationship to events
    events = db.relationship('Event', backref='dog', lazy=True, cascade='all, delete-orphan')
```

### Event Model
```python
class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.String(36), primary_key=True)
    dog_id = db.Column(db.String(36), db.ForeignKey('dogs.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # walk, poop, pee, vomit, nap
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    end_timestamp = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    bristol_stool_scale = db.Column(db.Integer, nullable=True)  # 1-7 for poop events
```

## 🔧 Configuration Management

### Environment-Based Configuration
```python
# config.py
class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET', os.urandom(24).hex())
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/dog_events_db')
    
    # Rate limiting
    DEFAULT_RATE_LIMITS = os.getenv('DEFAULT_RATE_LIMITS', '200 per day, 50 per hour')
    LOGIN_RATE_LIMIT = os.getenv('LOGIN_RATE_LIMIT', '5 per minute')
    
    # Security
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    WTF_CSRF_ENABLED = os.getenv('WTF_CSRF_ENABLED', 'True').lower() == 'true'
```

### Environment Variables
```bash
# .env file
FLASK_ENV=development
FLASK_SECRET=your-secure-secret-key
DATABASE_URL=postgresql://localhost/dog_events_dev

# Rate limiting
LOGIN_RATE_LIMIT=5 per minute
API_RATE_LIMIT=100 per hour

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/dog_events_tracker.log
```

### Database Setup Options

#### Option 1: Automated Setup (Recommended)
```bash
./setup-dev-db.sh
```

#### Option 2: Manual PostgreSQL Setup
```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
# macOS: brew services start postgresql
# Ubuntu: sudo systemctl start postgresql

# Create database
createdb dog_events_dev

# Configure .env file
cp env.example .env
# Edit DATABASE_URL in .env
```

#### Option 3: Docker PostgreSQL
```bash
docker run --name postgres-dev \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=dog_events_dev \
  -p 5432:5432 \
  -d postgres:15

# Update .env with: DATABASE_URL=postgresql://postgres:password@localhost:5432/dog_events_dev
```

## 🎨 Frontend Development

### Template System
```html
<!-- Base template: templates/main.html -->
{% extends "main.html" %}
{% block headtitle %}Page Title{% endblock %}
{% block body %}
    <!-- Page content -->
{% endblock %}
```

### Bootstrap 5 Components
- **Cards**: Dog profiles and event displays
- **Forms**: Input validation and styling
- **Tables**: Event listings with responsive design
- **Modals**: Confirmation dialogs for deletions
- **Responsive Grid**: Mobile-first design approach

### JavaScript Features
- **Form Validation**: Real-time feedback and character counters
- **Loading States**: Enhanced user experience during operations
- **Modal Management**: Bootstrap modal integration
- **Event Handling**: Dynamic form behavior

## 🔐 Authentication & Security

### User Roles
```python
class User(UserMixin, db.Model):
    role = db.Column(db.String(20), default='employee')  # admin, manager, employee
    
    # Role-based permissions
    # admin: Full access (create, read, update, delete)
    # manager: CRUD operations on dogs and events
    # employee: Read-only access
```

### Security Features
- **CSRF Protection**: Enabled on all forms
- **Rate Limiting**: Configurable limits per endpoint
- **Secure Cookies**: HTTPOnly, Secure, SameSite
- **Password Hashing**: bcrypt with salt
- **Input Validation**: WTForms with custom validators

### Rate Limiting Configuration
```python
@limiter.limit(application.config['LOGIN_RATE_LIMIT'])
def login():
    # Login endpoint with rate limiting

@limiter.limit(application.config['API_RATE_LIMIT'])
def api_dogs():
    # API endpoint with rate limiting
```

## 📝 Form Handling

### Dog Form
```python
class DogForm(FlaskForm):
    name = StringField('Dog Name', validators=[
        validators.InputRequired(),
        validators.Length(min=2, max=100),
        validators.Regexp(r'^[a-zA-Z\s\-\'\.]+$')
    ])
    
    size = SelectField('Size', choices=[
        ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')
    ])
```

### Event Form
```python
class EventForm(FlaskForm):
    event_type = SelectField('Event Type', choices=[
        ('walk', 'Walk'), ('poop', 'Poop'), ('pee', 'Pee'), 
        ('vomit', 'Vomit'), ('nap', 'Nap')
    ])
    
    bristol_stool_scale = SelectField('Bristol Stool Scale', choices=[
        ('1', '1 - Separate hard lumps'),
        ('2', '2 - Sausage-like but lumpy'),
        # ... more choices
    ])
```

## 🗄️ Database Operations

### CRUD Operations
```python
# Create
def create_dog(dog_data):
    dog = Dog.from_dict(dog_data)
    db.session.add(dog)
    db.session.commit()
    return dog.to_dict()

# Read
def get_dogs():
    return [dog.to_dict() for dog in Dog.query.all()]

# Update
def update_dog(dog_id, dog_data):
    dog = Dog.query.get(dog_id)
    for key, value in dog_data.items():
        setattr(dog, key, value)
    db.session.commit()
    return dog.to_dict()

# Delete
def delete_dog(dog_id):
    dog = Dog.query.get(dog_id)
    if dog:
        db.session.delete(dog)
        db.session.commit()
        return True
    return False
```

### Sample Data Initialization
```python
def init_sample_data():
    sample_dogs = [
        {
            'id': 'dog-001',
            'name': 'Max',
            'approx_age': '3 years',
            'size': 'medium',
            'breed_type': 'Golden Retriever'
        }
    ]
    
    for dog_data in sample_dogs:
        dog = Dog(**dog_data)
        db.session.add(dog)
    
    db.session.commit()
```

## 🧪 Testing & Development

### Health Check Endpoint
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "application": "healthy"
  }
}
```

### Sample Users
- **Admin**: `admin / Admin123!` (Full access)
- **Employee**: `employee / Employee123!` (Read-only)

### Development Workflow
1. **Make Changes**: Modify models, routes, or templates
2. **Test Locally**: Run `python3 run-dev.py`
3. **Database Changes**: Models auto-update on restart
4. **Verify Functionality**: Test all CRUD operations

## 🔍 Logging & Debugging

### Logging Configuration
```python
# Production logging with rotation
file_handler = RotatingFileHandler(
    application.config['LOG_FILE'], 
    maxBytes=application.config['LOG_MAX_SIZE'], 
    backupCount=application.config['LOG_BACKUP_COUNT']
)

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
application.logger.setLevel(getattr(logging, application.config['LOG_LEVEL']))
```

### Debug Information
```python
# Log application events
application.logger.info("Sample dog data initialized successfully")
application.logger.error(f"Error initializing sample data: {e}")

# Log API errors
application.logger.error(f"API error in api_dogs: {e}")
```

## 🚀 Performance Optimization

### Database Optimization
- **Indexing**: Add indexes on frequently queried fields
- **Connection Pooling**: Use connection pooling for PostgreSQL
- **Query Optimization**: Monitor slow queries

### Application Optimization
- **Caching**: Implement Redis for session storage
- **Static Files**: Configure nginx for static file serving
- **Worker Processes**: Use multiple Gunicorn workers

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check PostgreSQL service status
   pg_isready
   
   # Check database exists
   psql -l | grep dog_events_dev
   
   # Check environment variables
   echo $DATABASE_URL
   ```

2. **Import Errors**
   ```bash
   # Verify virtual environment
   which python
   
   # Check dependencies
   pip list | grep Flask
   ```

3. **Permission Errors**
   ```bash
   # Check logs directory
   mkdir -p logs
   chmod 755 logs
   
   # Check PostgreSQL permissions
   psql -U postgres -d dog_events_dev -c "SELECT 1;"
   ```

### Debug Mode
```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start with debug
python3 run-dev.py
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [WTForms Documentation](https://wtforms.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Happy developing! 🐕💻**
