#!/bin/bash

# Development Database Setup Script for Dog Events Tracker
# This script helps set up PostgreSQL for local development

set -e

echo "🐕 Setting up development database for Dog Events Tracker..."
echo "=================================================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed or not in PATH"
    echo ""
    echo "Please install PostgreSQL first:"
    echo "  macOS: brew install postgresql"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "  Windows: Download from https://www.postgresql.org/download/windows/"
    echo ""
    echo "Or use Docker:"
    echo "  docker run --name postgres-dev -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dog_events_dev -p 5432:5432 -d postgres:15"
    exit 1
fi

# Check if PostgreSQL service is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL service is not running"
    echo ""
    echo "Please start PostgreSQL service:"
    echo "  macOS: brew services start postgresql"
    echo "  Ubuntu/Debian: sudo systemctl start postgresql"
    echo "  Windows: Start PostgreSQL service from Services"
    exit 1
fi

# Database configuration
DB_NAME="dog_events_dev"
DB_USER="postgres"
DB_PASSWORD="password"

echo "✅ PostgreSQL is running"
echo ""

# Create database if it doesn't exist
if psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "✅ Database '$DB_NAME' already exists"
else
    echo "📝 Creating database '$DB_NAME'..."
    createdb $DB_NAME
    echo "✅ Database '$DB_NAME' created successfully"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Dog Events Tracker Development Configuration
FLASK_ENV=development
FLASK_SECRET=dev-secret-key-change-in-production
DATABASE_URL=postgresql://localhost/$DB_NAME
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600
DEBUG=True
TESTING=False
DEFAULT_RATE_LIMITS=200 per day, 50 per hour
LOGIN_RATE_LIMIT=5 per minute
REGISTER_RATE_LIMIT=3 per hour
ADD_EDIT_RATE_LIMIT=10 per minute
DELETE_RATE_LIMIT=5 per minute
API_RATE_LIMIT=100 per hour
LOG_LEVEL=DEBUG
LOG_FILE=logs/dog_events_tracker.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=10
EOF
    echo "✅ .env file created with development configuration"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs
echo "✅ Logs directory created"

echo ""
echo "🎉 Development database setup complete!"
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Start the application: python3 run-dev.py"
echo "3. Access the app at: http://localhost:8080"
echo ""
echo "Database connection: postgresql://localhost/$DB_NAME"
echo "Sample users:"
echo "  - Admin: admin / Admin123!"
echo "  - Employee: employee / Employee123!"
echo ""
echo "Happy developing! 🐕💻"
