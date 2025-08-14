#!/usr/bin/env python3
"""
Test script to verify the Flask application works
"""
import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

def test_application():
    """Test the application without starting the server"""
    try:
        from application import application, db, Employee
        
        print("✅ Application imported successfully")
        
        # Test database connection
        with application.app_context():
            print("✅ Application context created")
            
            # Create tables
            db.create_all()
            print("✅ Database tables created")
            
            # Check if sample data exists
            employee_count = Employee.query.count()
            print(f"✅ Employee count: {employee_count}")
            
            if employee_count == 0:
                print("ℹ️  No employees found - this is expected for a fresh database")
            else:
                employees = Employee.query.all()
                print(f"✅ Found {len(employees)} employees:")
                for emp in employees:
                    print(f"   - {emp.fullname} ({emp.job_title})")
            
            print("\n🎉 Application test completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error testing application: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_application()
