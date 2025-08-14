#!/bin/bash

# Employee Directory Serverless Deployment Script
# This script automates the deployment of the Lambda application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGE=${1:-dev}
REGION=${2:-us-east-1}
STACK_NAME="employee-directory-${STAGE}"

echo -e "${BLUE}🚀 Employee Directory Serverless Deployment${NC}"
echo -e "${BLUE}==========================================${NC}"
echo -e "Stage: ${YELLOW}${STAGE}${NC}"
echo -e "Region: ${YELLOW}${REGION}${NC}"
echo -e "Stack: ${YELLOW}${STACK_NAME}${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if serverless framework is installed
if ! command -v serverless &> /dev/null; then
    echo -e "${YELLOW}⚠️  Serverless framework not found. Installing...${NC}"
    npm install -g serverless
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
npm install
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Set up environment variables
echo -e "${BLUE}🔧 Setting up environment variables...${NC}"

# Check if SSM parameters exist
DB_URL_PARAM="/employee-directory/${STAGE}/database-url"
SECRET_PARAM="/employee-directory/${STAGE}/flask-secret"

# Create database URL parameter if it doesn't exist
if ! aws ssm get-parameter --name "$DB_URL_PARAM" --region "$REGION" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Database URL parameter not found. Creating...${NC}"
    
    if [ "$STAGE" = "dev" ]; then
        # For dev, use SQLite
        DB_URL="sqlite:///employees.db"
    else
        # For staging/prod, prompt for Aurora endpoint
        echo -e "${YELLOW}Please enter your Aurora Serverless endpoint:${NC}"
        read -p "Database endpoint: " AURORA_ENDPOINT
        echo -e "${YELLOW}Please enter your database name:${NC}"
        read -p "Database name: " DB_NAME
        echo -e "${YELLOW}Please enter your database username:${NC}"
        read -p "Username: " DB_USER
        echo -e "${YELLOW}Please enter your database password:${NC}"
        read -s -p "Password: " DB_PASSWORD
        echo ""
        
        DB_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${AURORA_ENDPOINT}:5432/${DB_NAME}"
    fi
    
    aws ssm put-parameter \
        --name "$DB_URL_PARAM" \
        --value "$DB_URL" \
        --type "SecureString" \
        --region "$REGION" \
        --description "Database connection string for Employee Directory ${STAGE}"
    
    echo -e "${GREEN}✅ Database URL parameter created${NC}"
else
    echo -e "${GREEN}✅ Database URL parameter exists${NC}"
fi

# Create Flask secret parameter if it doesn't exist
if ! aws ssm get-parameter --name "$SECRET_PARAM" --region "$REGION" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Flask secret parameter not found. Creating...${NC}"
    
    # Generate a random secret
    FLASK_SECRET=$(openssl rand -base64 32)
    
    aws ssm put-parameter \
        --name "$SECRET_PARAM" \
        --value "$FLASK_SECRET" \
        --type "SecureString" \
        --region "$REGION" \
        --description "Flask secret key for Employee Directory ${STAGE}"
    
    echo -e "${GREEN}✅ Flask secret parameter created${NC}"
else
    echo -e "${GREEN}✅ Flask secret parameter exists${NC}"
fi

echo -e "${GREEN}✅ Environment variables configured${NC}"
echo ""

# Deploy the application
echo -e "${BLUE}🚀 Deploying application...${NC}"
serverless deploy --stage "$STAGE" --region "$REGION" --verbose

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    
    # Get deployment outputs
    echo -e "${BLUE}📊 Deployment outputs:${NC}"
    serverless info --stage "$STAGE" --region "$REGION"
    
    echo ""
    echo -e "${GREEN}🎉 Employee Directory deployed successfully to ${STAGE} environment!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Test the application using the API Gateway URL above"
    echo -e "2. Upload static assets to the S3 bucket"
    echo -e "3. Configure CloudFront distribution"
    echo -e "4. Set up monitoring and alerts"
    
else
    echo -e "${RED}❌ Deployment failed!${NC}"
    exit 1
fi
