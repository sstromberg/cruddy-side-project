# Production Deployment Guide

## 🚀 **Dog Events Tracker - Production Deployment**

This guide covers deploying the Dog Events Tracker application to production environments.

## 📋 **Prerequisites**

- Python 3.11+ installed
- Virtual environment setup
- Production database (PostgreSQL recommended)
- Reverse proxy (nginx/Apache) for production
- SSL certificate for HTTPS

## 🔧 **Installation Steps**

### 1. **Clone and Setup**
```bash
git clone <repository-url>
cd directory-frontend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Environment Configuration**
```bash
cp env.example .env
# Edit .env with your production values
```

### 4. **Database Setup**
```bash
# For PostgreSQL (recommended)
export DATABASE_URL="postgresql://username:password@localhost/dog_events_db"

# For SQLite (development only)
export DATABASE_URL="sqlite:///dogs.db"
```

## ⚙️ **Environment Variables**

### **Required Variables**
```bash
FLASK_ENV=production
FLASK_SECRET=your-super-secure-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/dog_events_db
```

### **Security Configuration**
```bash
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=True
```

### **Rate Limiting**
```bash
DEFAULT_RATE_LIMITS=200 per day, 50 per hour
LOGIN_RATE_LIMIT=5 per minute
REGISTER_RATE_LIMIT=3 per hour
ADD_EDIT_RATE_LIMIT=10 per minute
DELETE_RATE_LIMIT=5 per minute
API_RATE_LIMIT=100 per hour
```

### **Logging Configuration**
```bash
LOG_LEVEL=INFO
LOG_FILE=logs/dog_events_tracker.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=10
```

## 🚀 **Starting the Application**

### **Option 1: Direct Python (Development)**
```bash
python3 run-production.py
```

### **Option 2: Gunicorn (Production)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 "app.application:application"
```

### **Option 3: Waitress (Windows Production)**
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8080 "app.application:application"
```

## 🔒 **Security Considerations**

### **1. Secret Key**
- Generate a strong secret key: `python3 -c "import secrets; print(secrets.token_hex(32))"`
- Never commit secrets to version control
- Use environment variables for all sensitive data

### **2. Database Security**
- Use strong database passwords
- Limit database access to application server only
- Enable SSL for database connections in production

### **3. HTTPS Configuration**
- Always use HTTPS in production
- Configure proper SSL certificates
- Set security headers appropriately

## 📊 **Monitoring and Health Checks**

### **Health Check Endpoint**
```bash
curl http://your-domain/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "application": "healthy"
  }
}
```

### **Log Monitoring**
- Logs are written to `logs/dog_events_tracker.log`
- Log rotation is automatic (10MB max, 10 backups)
- Monitor for errors and unusual activity

## 🌐 **Reverse Proxy Configuration (nginx)**

### **Basic nginx Configuration**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/your/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Database Connection Errors**
   - Verify DATABASE_URL format
   - Check database server status
   - Verify user permissions

2. **Permission Errors**
   - Ensure logs directory is writable
   - Check file permissions for .env file

3. **Rate Limiting Issues**
   - Adjust rate limits in environment variables
   - Monitor for abuse patterns

### **Log Analysis**
```bash
# View recent errors
tail -f logs/dog_events_tracker.log | grep ERROR

# View access patterns
tail -f logs/dog_events_tracker.log | grep "INFO"
```

## 📈 **Performance Optimization**

### **Database Optimization**
- Use connection pooling for PostgreSQL
- Implement database indexing on frequently queried fields
- Monitor query performance

### **Application Optimization**
- Enable gunicorn workers based on CPU cores
- Use Redis for session storage in high-traffic scenarios
- Implement caching for static content

## 🚨 **Emergency Procedures**

### **Application Restart**
```bash
# Graceful restart
pkill -HUP gunicorn

# Force restart
pkill gunicorn
python3 run-production.py
```

### **Database Recovery**
- Regular database backups
- Test restore procedures
- Monitor database disk space

## 📞 **Support and Maintenance**

- Monitor application health regularly
- Keep dependencies updated
- Review security advisories
- Maintain backup procedures

---

**Last Updated**: January 2024  
**Version**: 1.0.0
