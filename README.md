# Dog Events Tracker

A modern, production-ready web application for tracking dog activities and events. Built with Flask and designed for both local development and production deployment.

## 🚀 Quick Start

### Local Development
```bash
cd directory-frontend

# Setup PostgreSQL database (recommended)
./setup-dev-db.sh

# Or manually setup PostgreSQL and create .env file
cp env.example .env
# Edit .env with your PostgreSQL connection details

# Install dependencies and start
pip install -r requirements.txt
python3 run-dev.py
```

### Production Deployment
```bash
cd directory-frontend
python3 run-production.py
# OR
gunicorn -w 4 -b 0.0.0.0:8080 "app.application:application"
```

## 🐕 Features

- **Dog Management**: Add, edit, and manage dog profiles
- **Event Tracking**: Record walks, bathroom breaks, naps, and more
- **Bristol Stool Scale**: Health monitoring for poop events
- **Location & Notes**: Optional tracking with detailed notes
- **User Authentication**: Role-based access control
- **Responsive UI**: Mobile-friendly Bootstrap 5 interface

## 🏗️ Architecture

- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (dev & production) - SQLite only for testing
- **Frontend**: Bootstrap 5 with responsive design
- **Authentication**: Flask-Login with bcrypt
- **Security**: CSRF protection, rate limiting, secure headers

## 📁 Project Structure

```
directory-frontend/
├── app/                    # Flask application
│   ├── application.py      # Main app, routes, models
│   ├── database.py         # Database models and operations
│   ├── config.py           # Configuration management
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, images
├── requirements.txt         # Production dependencies
├── run-dev.py              # Development server
├── run-production.py       # Production server
├── setup-dev-db.sh         # PostgreSQL setup script
├── env.example             # Environment configuration
└── PRODUCTION_DEPLOYMENT.md # Deployment guide
```

## 🔧 Configuration

### Environment Variables
```bash
FLASK_ENV=development
FLASK_SECRET=your-secure-secret-key
DATABASE_URL=postgresql://localhost/dog_events_dev
```

### Rate Limiting
```bash
LOGIN_RATE_LIMIT=5 per minute
API_RATE_LIMIT=100 per hour
```

## 🚀 Deployment

### Health Check
```bash
curl http://your-domain/health
```

### Production Server
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 "app.application:application"

# Using Waitress (Windows)
waitress-serve --host=0.0.0.0 --port=8080 "app.application:application"
```

## 📚 Documentation

- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide and technical details
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment and operations
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Detailed deployment guide

## 🔒 Security Features

- CSRF protection enabled
- Secure session cookies
- Rate limiting on all endpoints
- Role-based access control
- Input validation and sanitization
- SQL injection protection via ORM

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8080/health
```

### Sample Data
The application includes sample dogs and events for testing:
- **Admin User**: `admin / Admin123!`
- **Employee User**: `employee / Employee123!`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Happy dog tracking! 🐕✨**
