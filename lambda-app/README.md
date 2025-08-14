# Employee Directory - Serverless Lambda Application

This is the serverless version of the Employee Directory Application, designed to run on AWS Lambda with Aurora Serverless v2 database.

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Node.js 16+ and npm
- Python 3.9+
- Serverless Framework

### Installation
```bash
# Install serverless framework globally
npm install -g serverless

# Install project dependencies
npm install

# Deploy to dev environment
./deploy.sh dev
```

## 🏗️ Architecture

### Serverless Components
- **Lambda Functions**: Flask application wrapped with Mangum
- **API Gateway**: HTTP API for routing
- **Aurora Serverless v2**: PostgreSQL database that scales to zero
- **S3**: Static asset storage
- **CloudFront**: Global CDN for static assets
- **SSM Parameter Store**: Secure configuration management

### Cost Optimization
- **Pay-per-use**: Only pay for actual requests
- **Auto-scaling**: Automatically scales to zero when not in use
- **Database scaling**: Aurora Serverless v2 scales from 0.5 to 128 ACUs
- **Estimated monthly cost**: $9-28 (vs $60-105 for traditional deployment)

## 📁 Project Structure

```
lambda-app/
├── app/                    # Flask application
│   ├── __init__.py        # App factory
│   ├── models.py          # Database models
│   ├── routes.py          # Route definitions
│   └── utils.py           # Utility functions
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── handler.py              # Lambda entry point
├── static.py               # S3 event handler
├── serverless.yml          # Serverless configuration
├── aurora-serverless.yaml  # Aurora CloudFormation template
├── deploy.sh               # Deployment script
├── requirements.txt        # Python dependencies
└── package.json            # Node.js dependencies
```

## 🔧 Configuration

### Environment Variables
The application uses AWS SSM Parameter Store for configuration:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `/employee-directory/{stage}/database-url` | Database connection string | `postgresql://user:pass@host:5432/db` |
| `/employee-directory/{stage}/flask-secret` | Flask secret key | `random-secret-string` |

### Database Configuration
- **Development**: SQLite (local file)
- **Staging/Production**: Aurora Serverless v2 (PostgreSQL)

## 🚀 Deployment

### 1. Deploy Aurora Serverless (Optional)
```bash
# Deploy Aurora Serverless cluster
aws cloudformation create-stack \
  --stack-name employee-directory-aurora \
  --template-body file://aurora-serverless.yaml \
  --parameters ParameterKey=DBPassword,ParameterValue=YourSecurePassword123! \
  --capabilities CAPABILITY_IAM
```

### 2. Deploy Lambda Application
```bash
# Deploy to dev environment
./deploy.sh dev

# Deploy to staging
./deploy.sh staging

# Deploy to production
./deploy.sh prod
```

### 3. Manual Deployment
```bash
# Deploy using serverless framework
serverless deploy --stage dev --region us-east-1

# Deploy specific function
serverless deploy function --function api

# Remove deployment
serverless remove --stage dev
```

## 🧪 Testing

### Local Testing
```bash
# Test Lambda function locally
serverless invoke local -f api --data '{"httpMethod": "GET", "path": "/"}'

# Start serverless offline
serverless offline start
```

### Integration Testing
```bash
# Test deployed API
curl -X GET https://your-api-id.execute-api.us-east-1.amazonaws.com/

# Test specific endpoint
curl -X GET https://your-api-id.execute-api.us-east-1.amazonaws.com/api/employees
```

## 📊 Monitoring

### CloudWatch Logs
```bash
# View function logs
serverless logs -f api --stage dev

# Follow logs in real-time
serverless logs -f api --stage dev --tail
```

### CloudWatch Metrics
- **Invocation count**: Number of function invocations
- **Duration**: Function execution time
- **Errors**: Error count and rate
- **Throttles**: Function throttling events

## 🔍 Troubleshooting

### Common Issues

#### Cold Start Latency
- **Symptom**: First request is slow
- **Solution**: Implement keep-warm functions or use Provisioned Concurrency

#### Database Connection Issues
- **Symptom**: Database connection errors
- **Solution**: Check VPC configuration and security groups

#### Memory Issues
- **Symptom**: Function timeouts or memory errors
- **Solution**: Increase memory allocation in serverless.yml

### Debug Mode
```bash
# Enable verbose logging
serverless deploy --stage dev --verbose

# Check function configuration
serverless info --stage dev
```

## 🔒 Security

### IAM Permissions
The application uses least-privilege IAM roles:
- **RDS access**: Database operations only
- **S3 access**: Static asset management only
- **SSM access**: Parameter retrieval only

### Network Security
- **VPC**: Lambda functions run in private subnets
- **Security Groups**: Restrictive access to database
- **Encryption**: Data encrypted at rest and in transit

## 📈 Scaling

### Automatic Scaling
- **Lambda**: Scales automatically based on request volume
- **Aurora**: Scales from 0.5 to 128 ACUs automatically
- **API Gateway**: Handles concurrent requests automatically

### Performance Optimization
- **Connection pooling**: Database connection reuse
- **Caching**: CloudFront caching for static assets
- **Compression**: Automatic gzip compression

## 🚀 Future Enhancements

### Planned Features
- **WebSocket support**: Real-time updates
- **GraphQL API**: Flexible data querying
- **Advanced caching**: Redis integration
- **Monitoring**: Enhanced observability

### Technical Improvements
- **Multi-region**: Global deployment
- **Blue-green**: Zero-downtime deployments
- **Canary**: Gradual rollouts
- **Chaos engineering**: Resilience testing

## 📚 Additional Resources

- [Serverless Framework Documentation](https://www.serverless.com/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Aurora Serverless Documentation](https://docs.aws.amazon.com/aurora/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Make changes
3. Test locally
4. Deploy to dev environment
5. Create pull request

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Include tests for new features
- Update documentation

---

**Happy serverless coding! 🎉**
