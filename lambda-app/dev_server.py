#!/usr/bin/env python3
"""
Development server for Lambda Flask application
Runs the same Flask app as production but with a standard WSGI server
"""
import os
import sys
from pathlib import Path

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://localhost:5432/employee_directory_dev'
os.environ['FLASK_SECRET'] = 'dev-secret-key-change-in-production'

def main():
    """Start the development server"""
    try:
        from app import create_app
        
        print("🚀 Starting Lambda Flask Development Server")
        print("=" * 50)
        print(f"Database: {os.environ.get('DATABASE_URL')}")
        print(f"URL: http://localhost:8080")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print()
        
        # Create Flask app
        app = create_app()
        
        # Run the development server
        app.run(
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
