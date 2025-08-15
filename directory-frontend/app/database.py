"""
Database abstraction layer supporting both SQLite (local) and PostgreSQL (production)
"""
import os
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dogs.db')
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'

# Initialize SQLAlchemy
db = SQLAlchemy()
Base = declarative_base()

class Dog(db.Model):
    """Dog model for both local and production databases"""
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
    
    @classmethod
    def from_dict(cls, data):
        """Create dog from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            approx_age=data.get('approx_age'),
            size=data.get('size'),
            breed_type=data.get('breed_type')
        )

class Event(db.Model):
    """Event model for both local and production databases"""
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
    
    @classmethod
    def from_dict(cls, data):
        """Create event from dictionary"""
        return cls(
            id=data.get('id'),
            dog_id=data.get('dog_id'),
            event_type=data.get('event_type'),
            timestamp=data.get('timestamp'),
            end_timestamp=data.get('end_timestamp'),
            location=data.get('location'),
            notes=data.get('notes'),
            bristol_stool_scale=data.get('bristol_stool_scale')
        )

def init_database(app):
    """Initialize database with app context"""
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add sample data if table is empty
        if Dog.query.count() == 0:
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
                dog = Dog.from_dict(dog_data)
                db.session.add(dog)
            
            db.session.commit()
        
        if Event.query.count() == 0:
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
                event = Event.from_dict(event_data)
                db.session.add(event)
            
            db.session.commit()

def get_dogs():
    """Get all dogs"""
    return [dog.to_dict() for dog in Dog.query.all()]

def get_dog(dog_id):
    """Get dog by ID"""
    dog = Dog.query.get(dog_id)
    return dog.to_dict() if dog else None

def create_dog(dog_data):
    """Create new dog"""
    import uuid
    if not dog_data.get('id'):
        dog_data['id'] = f"dog-{str(uuid.uuid4())[:8]}"
    
    dog = Dog.from_dict(dog_data)
    db.session.add(dog)
    db.session.commit()
    return dog.to_dict()

def update_dog(dog_id, dog_data):
    """Update existing dog"""
    dog = Dog.query.get(dog_id)
    if not dog:
        return None
    
    for key, value in dog_data.items():
        if key != 'id' and hasattr(dog, key):
            setattr(dog, key, value)
    
    db.session.commit()
    return dog.to_dict()

def delete_dog(dog_id):
    """Delete dog"""
    dog = Dog.query.get(dog_id)
    if dog:
        db.session.delete(dog)
        db.session.commit()
        return True
    return False

def get_dog_events(dog_id):
    """Get events for a specific dog"""
    events = Event.query.filter_by(dog_id=dog_id).order_by(Event.timestamp.desc()).all()
    return [event.to_dict() for event in events]

def create_event(event_data):
    """Create new event"""
    import uuid
    if not event_data.get('id'):
        event_data['id'] = f"evt-{str(uuid.uuid4())[:8]}"
    
    event = Event.from_dict(event_data)
    db.session.add(event)
    db.session.commit()
    return event.to_dict()

def update_event(event_id, event_data):
    """Update existing event"""
    event = Event.query.get(event_id)
    if not event:
        return None
    
    for key, value in event_data.items():
        if key != 'id' and hasattr(event, key):
            setattr(event, key, value)
    
    db.session.commit()
    return event.to_dict()

def delete_event(event_id):
    """Delete event"""
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        return True
    return False
