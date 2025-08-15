#!/usr/bin/env python3
"""
Production server runner for Dog Events Tracker
Run this script to start the application in production mode
"""
import os
import sys
from pathlib import Path

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///dogs.db')
os.environ['FLASK_SECRET'] = os.getenv('FLASK_SECRET', os.urandom(24).hex())

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

def main():
    """Main production startup function"""
    try:
        # Import application after environment is set
        from app.application import application, db
        
        print("🚀 Starting Dog Events Tracker Production Server")
        print("=" * 50)
        print(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
        print(f"Database: {os.environ.get('DATABASE_URL', 'sqlite:///dogs.db')}")
        print(f"Debug Mode: {application.debug}")
        print(f"Log Level: {application.config.get('LOG_LEVEL', 'INFO')}")
        print("=" * 50)
        
        # Initialize database
        with application.app_context():
            db.create_all()
            print("✅ Database initialized successfully")
        
        # Start production server
        application.run(
            host="0.0.0.0", 
            port=int(os.getenv('PORT', 8080)), 
            debug=False,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
