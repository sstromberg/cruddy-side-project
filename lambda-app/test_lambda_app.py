#!/usr/bin/env python3
"""
Test script to verify the Lambda Flask application works
"""
import os
import sys

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://localhost:5432/employee_directory_dev'
os.environ['FLASK_SECRET'] = 'dev-secret-key-change-in-production'

def test_lambda_app():
    """Test the Lambda Flask application"""
    try:
        from app import create_app
        from app.models import Employee
        
        print("✅ Lambda app imported successfully")
        
        # Create Flask app
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test database connection
        with app.app_context():
            print("✅ App context created")
            
            # Test getting employees
            employees = Employee.query.all()
            print(f"✅ Found {len(employees)} employees:")
            for emp in employees:
                print(f"   - {emp.fullname} ({emp.job_title})")
            
            print("\n🎉 Lambda app test completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error testing Lambda app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_lambda_app()
