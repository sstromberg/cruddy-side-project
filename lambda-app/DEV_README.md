# Employee Directory - Development Environment

This directory contains the **production-ready Lambda application** that can be run locally for development.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Node.js 16+ (for serverless deployment)

### 1. Install Dependencies
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Node.js dependencies (for production deployment)
npm install
```

### 2. Start Development Server
```bash
# Start the development environment (recommended)
./start-dev.sh

# Or manually:
export DATABASE_URL="postgresql://localhost:5432/employee_directory_dev"
export FLASK_SECRET="dev-secret-key-change-in-production"
python3 dev_server.py
```

### 3. Access the Application
- **Main Application**: http://localhost:8080
- **API Endpoint**: http://localhost:8080/api/employees
- **Add Employee**: http://localhost:8080/add

## 🏗️ Architecture

### Development vs Production
- **Development**: Flask WSGI server with PostgreSQL
- **Production**: AWS Lambda + API Gateway + Aurora Serverless

### Database
- **Development**: Local PostgreSQL (`employee_directory_dev`)
- **Production**: Aurora Serverless v2 (PostgreSQL)

### Key Benefits
- ✅ **Same Code**: Uses exact same Flask app as production
- ✅ **PostgreSQL**: No more SQLite file locking issues
- ✅ **Reliable**: Stable development environment
- ✅ **Fast**: No cold starts or serverless overhead
- ✅ **Debuggable**: Standard Flask development server

## 🧪 Testing

### Test Application
```bash
# Test the Lambda app directly
python3 test_lambda_app.py
```

### API Testing
```bash
# Get all employees
curl http://localhost:8080/api/employees

# Get specific employee
curl http://localhost:8080/api/employees/emp-001
```

### Manual Testing
1. Open http://localhost:8080 in your browser
2. Test CRUD operations:
   - View employee list
   - Add new employee
   - Edit existing employee
   - Delete employee

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL="postgresql://localhost:5432/employee_directory_dev"
FLASK_SECRET="dev-secret-key-change-in-production"
```

### Database Setup
```bash
# Start PostgreSQL
brew services start postgresql@14

# Create database
createdb employee_directory_dev
```

## 📁 Project Structure

```
lambda-app/
├── app/                    # Flask application (same as production)
│   ├── __init__.py        # App factory
│   ├── models.py          # Database models
│   ├── routes.py          # Route definitions
│   └── utils.py           # Utility functions
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── dev_server.py          # Development server
├── test_lambda_app.py     # Application testing
├── start-dev.sh           # Development setup script
├── handler.py             # Lambda entry point (production)
├── serverless.yml         # Serverless configuration
└── requirements.txt       # Python dependencies
```

## 🚀 Deployment

### Development Testing
```bash
./start-dev.sh
```

### Production Deployment
```bash
# Deploy to AWS
./deploy.sh prod
```

## 🔍 Troubleshooting

### PostgreSQL Issues
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL
brew services start postgresql@14

# Create database
createdb employee_directory_dev
```

### Python Dependencies
```bash
# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall
```

### Database Connection
```bash
# Test database connection
psql -h localhost -d employee_directory_dev -c "SELECT 1;"
```

## 🎯 Why This Approach?

### Problems with Original Development
- ❌ SQLite file locking issues
- ❌ Flask dev server blocking
- ❌ Different database technology
- ❌ Unreliable server startup

### Benefits of New Approach
- ✅ **Production Parity**: Same Flask app, same database
- ✅ **Reliability**: PostgreSQL client-server architecture
- ✅ **Performance**: No file I/O blocking
- ✅ **Scalability**: Can handle concurrent requests
- ✅ **Debugging**: Standard Flask development tools

## 🚀 Next Steps

1. **Start Development**: Run `./start-dev.sh`
2. **Test Features**: Verify all CRUD operations work
3. **Make Changes**: Modify templates, routes, or models
4. **Deploy**: Use `./deploy.sh prod` for production

---

**Happy coding! 🎉**
