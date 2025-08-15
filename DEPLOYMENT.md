# Deployment Guide

## 🚀 Production Deployment

This guide covers deploying the Dog Events Tracker application to production environments.

## 📋 Prerequisites

- Python 3.11+ installed
- Virtual environment setup
- Production database (PostgreSQL required)
- Reverse proxy (nginx/Apache) for production
- SSL certificate for HTTPS
- Domain name configured

## 🔧 Installation & Setup

### 1. **Clone and Setup**
```bash
git clone <repository-url>
cd containerized_apps_aws/directory-frontend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt

# For production server (choose one)
pip install gunicorn      # Linux/macOS
pip install waitress      # Windows
```

### 3. **Environment Configuration**
```bash
cp env.example .env
# Edit .env with your production values
```

### 4. **Database Setup**
```bash
# PostgreSQL is required for production
export DATABASE_URL="postgresql://username:password@localhost/dog_events_prod"

# Create production database
createdb dog_events_prod
```

## ⚙️ Environment Variables

### **Required Variables**
```bash
FLASK_ENV=production
FLASK_SECRET=your-super-secure-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/dog_events_prod
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

## 🚀 Starting the Application

### **Option 1: Direct Python (Development)**
```bash
python3 run-production.py
```

### **Option 2: Gunicorn (Production - Linux/macOS)**
```bash
gunicorn -w 4 -b 0.0.0.0:8080 "app.application:application"
```

### **Option 3: Waitress (Production - Windows)**
```bash
waitress-serve --host=0.0.0.0 --port=8080 "app.application:application"
```

### **Option 4: Systemd Service (Linux)**
```bash
# Create service file
sudo nano /etc/systemd/system/dog-events-tracker.service

[Unit]
Description=Dog Events Tracker
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/gunicorn -w 4 -b 0.0.0.0:8080 "app.application:application"
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable dog-events-tracker
sudo systemctl start dog-events-tracker
```

## 🔒 Security Considerations

### **1. Secret Key Management**
```bash
# Generate strong secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Set in environment
export FLASK_SECRET="your-generated-secret-key"
```

### **2. Database Security**
- Use strong database passwords
- Limit database access to application server only
- Enable SSL for database connections in production
- Use connection pooling for better performance

### **3. HTTPS Configuration**
- Always use HTTPS in production
- Configure proper SSL certificates (Let's Encrypt)
- Set security headers appropriately
- Enable HTTP/2 for better performance

### **4. Firewall Configuration**
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP (redirect to HTTPS)
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## 📊 Monitoring and Health Checks

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
- Set up log aggregation (ELK stack, Graylog, etc.)

### **Performance Monitoring**
```bash
# Monitor application performance
htop
iotop
netstat -tulpn

# Monitor database performance
pg_stat_statements  # PostgreSQL
```

## 🌐 Reverse Proxy Configuration

### **nginx Configuration**
```nginx
# /etc/nginx/sites-available/dog-events-tracker
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Proxy Configuration
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static Files
    location /static/ {
        alias /path/to/your/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
    }
    
    # Health Check
    location /health {
        proxy_pass http://127.0.0.1:8080;
        access_log off;
    }
}
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Database Connection Errors**
   ```bash
   # Verify database connectivity
   psql -h localhost -U username -d dog_events_prod -c "SELECT 1;"
   
   # Check database server status
   sudo systemctl status postgresql
   ```

2. **Permission Errors**
   ```bash
   # Ensure logs directory is writable
   sudo chown -R www-data:www-data /path/to/your/app
   sudo chmod -R 755 /path/to/your/app
   
   # Check file permissions
   ls -la .env
   ```

3. **Rate Limiting Issues**
   ```bash
   # Adjust rate limits in environment variables
   export LOGIN_RATE_LIMIT="10 per minute"
   
   # Monitor for abuse patterns
   tail -f logs/dog_events_tracker.log | grep "429"
   ```

### **Log Analysis**
```bash
# View recent errors
tail -f logs/dog_events_tracker.log | grep ERROR

# View access patterns
tail -f logs/dog_events_tracker.log | grep "INFO"

# Monitor rate limiting
tail -f logs/dog_events_tracker.log | grep "429"
```

## 📈 Performance Optimization

### **Database Optimization**
```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_dogs_name ON dogs(name);
CREATE INDEX idx_events_dog_id ON events(dog_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_event_type ON events(event_type);
```

### **Application Optimization**
```bash
# Optimize Gunicorn workers
# Rule of thumb: (2 x num_cores) + 1
gunicorn -w 5 -b 0.0.0.0:8080 --worker-class gevent "app.application:application"

# Enable connection pooling
export DATABASE_URL="postgresql://user:pass@localhost/dogs_db?pool_size=20&max_overflow=30"
```

## 🚨 Emergency Procedures

### **Application Restart**
```bash
# Graceful restart
sudo systemctl reload dog-events-tracker

# Force restart
sudo systemctl restart dog-events-tracker

# Manual restart
pkill gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 "app.application:application"
```

### **Database Recovery**
```bash
# Create backup
pg_dump -h localhost -U username dog_events_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -h localhost -U username dog_events_prod < backup_file.sql
```

## 📞 Support and Maintenance

### **Regular Maintenance Tasks**
- Monitor log files for errors
- Check database performance
- Update dependencies monthly
- Review security advisories
- Test backup and recovery procedures

---

**Last Updated**: January 2024  
**Version**: 1.0.0
