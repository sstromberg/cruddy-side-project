#!/usr/bin/env python3
"""
Data Migration Script for Employee Directory
Migrates data from SQLite to Aurora Serverless PostgreSQL
"""

import sqlite3
import psycopg2
import json
import os
import sys
from urllib.parse import urlparse

def connect_sqlite(db_path):
    """Connect to SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        return None

def connect_postgres(database_url):
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def get_sqlite_data(sqlite_conn):
    """Extract data from SQLite database"""
    try:
        cursor = sqlite_conn.cursor()
        
        # Get table schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='employees'")
        schema = cursor.fetchone()
        print(f"SQLite schema: {schema[0] if schema else 'No schema found'}")
        
        # Get employee data
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        
        print(f"Found {len(employees)} employees in SQLite")
        
        # Convert to list of dictionaries
        employee_data = []
        for emp in employees:
            employee_dict = dict(emp)
            # Parse badges JSON if it exists
            if employee_dict.get('badges'):
                try:
                    badges = json.loads(employee_dict['badges'])
                    employee_dict['badges'] = badges
                except json.JSONDecodeError:
                    employee_dict['badges'] = []
            else:
                employee_dict['badges'] = []
            
            employee_data.append(employee_dict)
        
        return employee_data
        
    except Exception as e:
        print(f"Error extracting data from SQLite: {e}")
        return []

def create_postgres_schema(postgres_conn):
    """Create PostgreSQL schema"""
    try:
        cursor = postgres_conn.cursor()
        
        # Create employees table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS employees (
            id VARCHAR(36) PRIMARY KEY,
            fullname VARCHAR(100) NOT NULL,
            location VARCHAR(100) NOT NULL,
            job_title VARCHAR(100) NOT NULL,
            badges TEXT
        );
        """
        
        cursor.execute(create_table_sql)
        postgres_conn.commit()
        print("PostgreSQL schema created successfully")
        
    except Exception as e:
        print(f"Error creating PostgreSQL schema: {e}")
        postgres_conn.rollback()

def insert_postgres_data(postgres_conn, employees):
    """Insert data into PostgreSQL"""
    try:
        cursor = postgres_conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM employees")
        print("Cleared existing PostgreSQL data")
        
        # Insert new data
        insert_sql = """
        INSERT INTO employees (id, fullname, location, job_title, badges)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        for emp in employees:
            cursor.execute(insert_sql, (
                emp['id'],
                emp['fullname'],
                emp['location'],
                emp['job_title'],
                json.dumps(emp['badges'])
            ))
        
        postgres_conn.commit()
        print(f"Successfully inserted {len(employees)} employees into PostgreSQL")
        
    except Exception as e:
        print(f"Error inserting data into PostgreSQL: {e}")
        postgres_conn.rollback()

def verify_migration(postgres_conn, expected_count):
    """Verify the migration was successful"""
    try:
        cursor = postgres_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        actual_count = cursor.fetchone()[0]
        
        if actual_count == expected_count:
            print(f"✅ Migration verified: {actual_count} employees found")
            return True
        else:
            print(f"❌ Migration verification failed: expected {expected_count}, got {actual_count}")
            return False
            
    except Exception as e:
        print(f"Error verifying migration: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Employee Directory Data Migration")
    print("====================================")
    
    # Configuration
    sqlite_path = input("Enter path to SQLite database (default: ../directory-frontend/app/employees.db): ").strip()
    if not sqlite_path:
        sqlite_path = "../directory-frontend/app/employees.db"
    
    database_url = input("Enter PostgreSQL connection string: ").strip()
    if not database_url:
        print("❌ PostgreSQL connection string is required")
        sys.exit(1)
    
    # Validate connection strings
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found: {sqlite_path}")
        sys.exit(1)
    
    try:
        urlparse(database_url)
    except Exception as e:
        print(f"❌ Invalid PostgreSQL connection string: {e}")
        sys.exit(1)
    
    print(f"\n📊 Migration Configuration:")
    print(f"SQLite: {sqlite_path}")
    print(f"PostgreSQL: {database_url.split('@')[1] if '@' in database_url else 'Invalid URL'}")
    
    # Confirm migration
    confirm = input("\nProceed with migration? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Migration cancelled")
        sys.exit(0)
    
    print("\n🔄 Starting migration...")
    
    # Connect to databases
    print("Connecting to SQLite...")
    sqlite_conn = connect_sqlite(sqlite_path)
    if not sqlite_conn:
        print("❌ Failed to connect to SQLite")
        sys.exit(1)
    
    print("Connecting to PostgreSQL...")
    postgres_conn = connect_postgres(database_url)
    if not postgres_conn:
        print("❌ Failed to connect to PostgreSQL")
        sqlite_conn.close()
        sys.exit(1)
    
    try:
        # Extract data from SQLite
        print("\n📥 Extracting data from SQLite...")
        employees = get_sqlite_data(sqlite_conn)
        if not employees:
            print("❌ No data found in SQLite")
            sys.exit(1)
        
        # Create PostgreSQL schema
        print("\n🏗️  Creating PostgreSQL schema...")
        create_postgres_schema(postgres_conn)
        
        # Insert data into PostgreSQL
        print("\n📤 Inserting data into PostgreSQL...")
        insert_postgres_data(postgres_conn, employees)
        
        # Verify migration
        print("\n✅ Verifying migration...")
        if verify_migration(postgres_conn, len(employees)):
            print("\n🎉 Migration completed successfully!")
            print(f"   {len(employees)} employees migrated")
            print("\nNext steps:")
            print("1. Update your DATABASE_URL environment variable")
            print("2. Test the application with the new database")
            print("3. Verify all functionality works correctly")
        else:
            print("\n❌ Migration verification failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
        
    finally:
        # Clean up connections
        if sqlite_conn:
            sqlite_conn.close()
        if postgres_conn:
            postgres_conn.close()

if __name__ == "__main__":
    main()
