#!/bin/bash

# Employee Directory Development Setup Script
# This script sets up the local development environment

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Employee Directory Development Setup${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 not found. Please install Python 3.9+ first.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip3 not found. Please install pip first.${NC}"
    exit 1
fi

echo -e "${BLUE}🔧 Setting up development environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install -r requirements-dev.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Some dependencies may not have installed correctly${NC}"
fi

# Create .env file for development
cat > .env << EOF
FLASK_ENV=development
DATABASE_URL=sqlite:///employees.db
FLASK_SECRET=$(python3.11 -c "import secrets; print(secrets.token_hex(24))")
EOF

echo -e "${GREEN}✅ Environment file created${NC}"

# Deactivate virtual environment
deactivate

echo ""
echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Activate virtual environment: ${GREEN}source venv/bin/activate${NC}"
echo "2. Start the development server: ${GREEN}python3 run-dev.py${NC}"
echo "3. Open your browser to: ${GREEN}http://localhost:8080${NC}"
echo "4. The application will automatically create the SQLite database"
echo ""
echo -e "${BLUE}For production deployment:${NC}"
echo "1. Navigate to: ${GREEN}cd ../lambda-app${NC}"
echo "2. Run: ${GREEN}./deploy.sh prod${NC}"
echo ""
echo -e "${BLUE}Happy coding! 🎉${NC}"
