# Employee Directory Application

A modern, containerized employee directory application built with Flask and designed for both local development and AWS serverless production deployment.

## 🚀 Quick Start

### Option 1: Local Development (Recommended for Development)
```bash
# Navigate to development directory
cd directory-frontend

# Setup development environment
./setup-dev.sh

# Start the application
python3 run-dev.py

# Access the application
open http://localhost:8080
```

### Option 2: Serverless Production (Recommended for Production)
```bash
# Navigate to serverless directory
cd lambda-app

# Deploy to AWS
./deploy.sh prod

# Access the application via API Gateway URL
```

## 🏗️ Architecture

### Development Architecture
- **Backend**: Flask with SQLAlchemy
- **Database**: SQLite (local file-based)
- **Deployment**: Local Python server
- **Cost**: $0 (local development)

### Production Architecture
- **Backend**: AWS Lambda with Flask
- **Database**: Aurora Serverless v2 (PostgreSQL)
- **Deployment**: Serverless on AWS
- **Cost**: $9-28/month (60-80% savings vs traditional)

## 📁 Project Structure

```
containerized_apps_aws/
├── directory-frontend/          # Local development environment
│   ├── app/                     # Flask application
│   ├── templates/               # HTML templates
│   ├── static/                  # CSS, JS, images
│   ├── run-dev.py              # Development server runner
│   ├── setup-dev.sh            # Development setup script
│   └── requirements-dev.txt     # Development dependencies
├── lambda-app/                  # Serverless production deployment
│   ├── app/                     # Flask application (Lambda optimized)
│   ├── handler.py               # Lambda entry point
│   ├── serverless.yml           # Serverless framework config
│   ├── deploy.sh                # Production deployment script
│   └── README.md                # Serverless deployment guide
├── README.md                    # This file
├── COST_ANALYSIS.md             # Cost analysis and optimization
├── SERVERLESS_MIGRATION.md      # Serverless migration guide
└── REFACTORING_SUMMARY.md       # Complete refactoring summary
```

## 🎯 Features

### Core Functionality
- ✅ Employee management (CRUD operations)
- ✅ Badge system with visual indicators
- ✅ Responsive Bootstrap UI
- ✅ Form validation and error handling
- ✅ Flash message notifications

### Technical Features
- ✅ Automatic database initialization
- ✅ Sample data population
- ✅ Environment-based configuration
- ✅ Local development with SQLite
- ✅ Serverless production with Aurora

## 🔧 Configuration

### Development Environment
```bash
# Environment variables (auto-created by setup-dev.sh)
FLASK_ENV=development
DATABASE_URL=sqlite:///employees.db
FLASK_SECRET=dev-secret-key-change-in-production
```

### Production Environment
```bash
# Environment variables (managed by AWS SSM)
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@aurora-endpoint:5432/db
FLASK_SECRET=secure-random-string
```

## 🐳 Development vs Production

### Development (Local)
- **Setup**: `./setup-dev.sh` + `python3 run-dev.py`
- **Database**: SQLite (instant, no server)
- **Cost**: $0
- **Performance**: Excellent for development
- **Use Case**: Development, testing, demos

### Production (Serverless)
- **Setup**: `./deploy.sh prod`
- **Database**: Aurora Serverless v2
- **Cost**: $9-28/month
- **Performance**: Production-grade, auto-scaling
- **Use Case**: Production deployment, high availability

## 🚀 Deployment Options

### 1. Local Development
```bash
cd directory-frontend
./setup-dev.sh
python3 run-dev.py
```

### 2. AWS Serverless
```bash
cd lambda-app
./deploy.sh dev      # Development environment
./deploy.sh staging  # Staging environment
./deploy.sh prod     # Production environment
```

## 📊 Cost Comparison

| Environment | Monthly Cost | Annual Cost | Best For |
|-------------|--------------|-------------|----------|
| **Local Development** | $0 | $0 | Development, testing |
| **Serverless Production** | $9-28 | $114-348 | Production, scaling |
| **Traditional Container** | $55-97 | $660-1,164 | Legacy deployments |

## 🧪 Testing

### Local Testing
1. **Setup**: Run `./setup-dev.sh`
2. **Start**: Run `python3 run-dev.py`
3. **Access**: http://localhost:8080
4. **Test**: All CRUD operations

### Production Testing
1. **Deploy**: `./deploy.sh staging`
2. **Test**: API Gateway endpoints
3. **Monitor**: CloudWatch logs and metrics

## 🔍 Troubleshooting

### Development Issues
```bash
# Check dependencies
pip3 list | grep Flask

# Check database
ls -la employees.db

# Restart server
python3 run-dev.py
```

### Production Issues
```bash
# Check logs
serverless logs -f api

# Check status
serverless info

# Redeploy
serverless deploy
```

## 📚 Documentation

- [COST_ANALYSIS.md](COST_ANALYSIS.md) - Cost analysis and optimization
- [SERVERLESS_MIGRATION.md](SERVERLESS_MIGRATION.md) - Serverless migration guide
- [lambda-app/README.md](lambda-app/README.md) - Serverless deployment guide
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Complete refactoring summary

## 🚀 Next Steps

### For Developers
1. **Start Local**: Use `directory-frontend/` for development
2. **Test Features**: Verify all CRUD operations work
3. **Make Changes**: Modify templates, routes, or models

### For Deployment
1. **Choose Environment**: Development, staging, or production
2. **Deploy Serverless**: Use `lambda-app/` for AWS deployment
3. **Monitor Performance**: Set up CloudWatch alerts and monitoring

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Test locally with `directory-frontend/`
4. Deploy to staging with `lambda-app/`
5. Submit pull request

### Code Standards
- Follow PEP 8 for Python
- Use meaningful commit messages
- Include tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the comprehensive documentation
3. Create an issue in the repository
4. Contact the development team

---

**Choose your path:**
- 🖥️ **Local Development**: `directory-frontend/` for zero-cost development
- ☁️ **Serverless Production**: `lambda-app/` for scalable AWS deployment

**Happy coding! 🎉**
