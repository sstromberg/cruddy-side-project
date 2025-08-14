# Employee Directory Application - Deployment Guide

## Overview
This application has been refactored to use a unified database approach that works seamlessly in both local development and production AWS environments.

## Database Architecture

### Local Development
- **Database**: SQLite (file-based, no server required)
- **Benefits**: Zero configuration, instant startup, perfect for development
- **File**: `employees.db` (created automatically in the app directory)

### Production AWS
- **Database**: PostgreSQL (RDS or Aurora Serverless)
- **Benefits**: Scalable, reliable, cost-effective, AWS-native
- **Connection**: Uses `DATABASE_URL` environment variable

## Local Development

### Quick Start
```bash
# Start the application with SQLite
docker compose up --build

# Access the application
open http://localhost:8080
```

### Features
- ✅ Automatic database creation
- ✅ Sample employee data
- ✅ Full CRUD operations
- ✅ No external dependencies
- ✅ Instant startup

## Production AWS Deployment

### Option 1: ECS with RDS
```bash
# Deploy to ECS using the production compose file
docker compose -f docker-compose.prod.yml up -d

# Set environment variables
export FLASK_SECRET="your-secure-secret-here"
export DATABASE_URL="postgresql://user:pass@your-rds-endpoint:5432/employees"
```

### Option 2: EKS with Aurora Serverless
```bash
# Use the provided Kubernetes manifests
kubectl apply -f kubernetes/
```

### Option 3: EC2 with RDS
```bash
# Install Docker on EC2
# Copy the production compose file
# Set environment variables
# Run the application
```

## Environment Variables

| Variable | Local Default | Production Required |
|----------|---------------|-------------------|
| `FLASK_ENV` | `development` | `production` |
| `DATABASE_URL` | `sqlite:///employees.db` | PostgreSQL connection string |
| `FLASK_SECRET` | `dev-secret-key` | Secure random string |

## Database Migration

### From Local to Production
1. Export local data (if needed):
   ```bash
   sqlite3 employees.db ".dump" > backup.sql
   ```

2. Import to PostgreSQL:
   ```bash
   psql -h your-rds-endpoint -U username -d employees < backup.sql
   ```

### Schema Changes
The application automatically creates tables and handles schema migrations. No manual intervention required.

## Cost Optimization

### Development
- **Cost**: $0 (SQLite + local Docker)
- **Performance**: Excellent for development

### Production AWS
- **RDS**: ~$15-30/month for small instances
- **Aurora Serverless**: Pay-per-use, scales to zero
- **EC2**: ~$10-20/month for t3.small
- **Total**: ~$25-50/month for full production setup

## Monitoring and Scaling

### Health Checks
- Application health: `GET /health`
- Database connectivity: Built into the application

### Scaling
- **Horizontal**: Run multiple container instances behind ALB
- **Vertical**: Increase container resources
- **Database**: RDS Multi-AZ, Aurora Serverless v2

## Security

### Local Development
- SQLite file permissions
- Development-only secret key

### Production AWS
- RDS encryption at rest
- VPC security groups
- IAM roles for ECS/EKS
- Secrets Manager for credentials

## Troubleshooting

### Common Issues
1. **Database connection errors**: Check `DATABASE_URL` format
2. **Permission denied**: Ensure proper file permissions for SQLite
3. **Port conflicts**: Change port in docker-compose.yml

### Logs
```bash
# View application logs
docker compose logs directory-frontend

# View database logs (production)
docker compose logs postgres
```

## Next Steps

1. **Testing**: Verify local functionality
2. **CI/CD**: Set up automated testing and deployment
3. **Monitoring**: Add CloudWatch metrics and alarms
4. **Backup**: Configure automated database backups
5. **SSL**: Add HTTPS with ACM certificate
