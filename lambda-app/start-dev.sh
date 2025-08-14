#!/bin/bash

# Employee Directory Lambda Development Server
# This script starts the development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Employee Directory Lambda Development Server${NC}"
echo -e "${BLUE}==============================================${NC}"
echo ""

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  PostgreSQL is not running. Starting it...${NC}"
    brew services start postgresql@14
    sleep 3
fi

# Check if database exists
if ! psql -h localhost -U $(whoami) -lqt | cut -d \| -f 1 | grep -qw employee_directory_dev; then
    echo -e "${YELLOW}⚠️  Database 'employee_directory_dev' not found. Creating it...${NC}"
    createdb employee_directory_dev
fi

# Set environment variables
export DATABASE_URL="postgresql://localhost:5432/employee_directory_dev"
export FLASK_SECRET="dev-secret-key-change-in-production"

echo -e "${GREEN}✅ Environment setup complete${NC}"
echo -e "${GREEN}✅ Database: $DATABASE_URL${NC}"
echo ""

# Test the application
echo -e "${BLUE}🧪 Testing application...${NC}"
if python3 test_lambda_app.py; then
    echo -e "${GREEN}✅ Application test passed${NC}"
else
    echo -e "${RED}❌ Application test failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🚀 Starting development server...${NC}"
echo -e "${GREEN}URL: http://localhost:8080${NC}"
echo -e "${GREEN}API: http://localhost:8080/api/employees${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the development server
python3 dev_server.py
