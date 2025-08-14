# Developer Guide

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+ with Docker Compose
- Git for version control
- Code editor (VS Code, PyCharm, etc.)

### Development Setup
```bash
# Clone and start
git clone <repository-url>
cd containerized_apps_aws
docker compose up --build -d

# Access application
open http://localhost:8080
```

## 🏗️ Project Structure

```
directory-frontend/app/
├── application.py      # Main Flask app and routes
├── database.py         # Database models and operations
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
└── templates/          # HTML templates
```

## 🔧 Development Workflow

### Making Changes
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and test
docker compose up --build -d

# 3. Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### Testing Changes
1. **Start app**: `docker compose up --build -d`
2. **Access**: http://localhost:8080
3. **Test functionality**:
   - View employees
   - Add/edit/delete employees
   - Form validation
   - Error handling

## 🗄️ Database Development

### Adding New Fields
```python
# 1. Update model in database.py
class Employee(db.Model):
    # ... existing fields ...
    department = db.Column(db.String(100), nullable=True)

# 2. Update serialization methods
def to_dict(self):
    return {
        # ... existing fields ...
        'department': self.department,
    }

# 3. Update forms and templates
# The database will automatically create new columns
```

### Database Operations
```python
# CRUD operations are in database.py
get_employees()      # Get all employees
get_employee(id)     # Get specific employee
create_employee(data) # Create new employee
update_employee(id, data) # Update employee
delete_employee(id)   # Delete employee
```

## 🎨 Frontend Development

### Template System
```html
<!-- Base template: templates/main.html -->
{% extends "main.html" %}
{% block headtitle %}Page Title{% endblock %}
{% block body %}
    <!-- Page content -->
{% endblock %}
```

### Adding New Pages
```python
# 1. Add route in application.py
@application.route("/reports")
def reports():
    employees = get_employees()
    return render_template('reports.html', employees=employees)

# 2. Create template: templates/reports.html
# 3. Add navigation link
```

## 🐳 Docker Commands

### Essential Commands
```bash
# Start services
docker compose up -d

# View logs
docker compose logs directory-frontend

# Rebuild after changes
docker compose up --build -d

# Stop services
docker compose down

# Access container shell
docker compose exec directory-frontend /bin/bash
```

## 🔍 Debugging

### Common Issues
```bash
# Check logs
docker compose logs directory-frontend

# Check container status
docker compose ps

# Restart container
docker compose restart directory-frontend

# Check database
docker compose exec directory-frontend sqlite3 employees.db ".tables"
```

### Debug Mode
```python
# Enable in application.py
if __name__ == "__main__":
    application.run(host="0.0.0.0", port=80, debug=True)
```

## 🔧 Configuration

### Environment Variables
```bash
# Development (.env file)
FLASK_ENV=development
DATABASE_URL=sqlite:///employees.db
FLASK_SECRET=dev-secret-key

# Production
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/db
FLASK_SECRET=secure-random-string
```

## 📚 Best Practices

### Code Organization
- Keep models, views, and templates separate
- Use descriptive names for variables and functions
- Handle errors gracefully with try/catch blocks
- Validate all user input

### Security
- Use Flask-WTF for CSRF protection
- Never use raw SQL with user input
- Escape output in templates
- Use environment variables for secrets

### Performance
- Minimize database queries
- Use connection pooling in production
- Cache frequently accessed data
- Load data only when needed

## 🚀 Deployment

### Pre-deployment Checklist
- [ ] All functionality tested
- [ ] Environment variables configured
- [ ] Database migration tested
- [ ] Security review completed
- [ ] Documentation updated

### Production Commands
```bash
# Use production compose file
docker compose -f docker-compose.prod.yml up -d

# Set production environment variables
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@host:5432/db
export FLASK_SECRET=secure-random-string
```

---

For detailed information, see:
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
