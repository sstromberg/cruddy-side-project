#!/usr/bin/env python3.11
"""
Alternative development server runner for Employee Directory
Uses port 8080 with disabled reloader to avoid issues
"""
import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

# Set development environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///employees.db'
os.environ['FLASK_SECRET'] = os.urandom(24).hex()

def main():
    """Start the development server"""
    try:
        from application import application
        
        print("🚀 Starting Employee Directory Development Server (Alternative)")
        print("=" * 60)
        print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
        print(f"Database: {os.environ.get('DATABASE_URL', 'sqlite:///employees.db')}")
        print(f"URL: http://localhost:8080")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print()
        
        # Run the development server on port 8080
        application.run(
            host='127.0.0.1',
            port=8080,
            debug=True,
            use_reloader=False  # Disable reloader to avoid issues
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
