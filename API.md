# API Documentation

## Overview

The Employee Directory Application provides a web-based interface for managing employee information. While primarily designed as a web application, the underlying architecture supports future API development.

## Current Endpoints

### Web Routes

#### 1. Home Page
- **URL**: `/`
- **Method**: `GET`
- **Description**: Displays the main employee directory
- **Response**: HTML page with employee list

#### 2. Add Employee
- **URL**: `/add`
- **Method**: `GET`, `POST`
- **Description**: Form to add new employees
- **GET Response**: HTML form
- **POST Response**: Redirect to home page on success

#### 3. View Employee
- **URL**: `/view/<employee_id>`
- **Method**: `GET`
- **Description**: Display employee details
- **Response**: HTML page with employee information

#### 4. Edit Employee
- **URL**: `/edit/<employee_id>`
- **Method**: `GET`, `POST`
- **Description**: Form to edit existing employees
- **GET Response**: HTML form pre-filled with employee data
- **POST Response**: Redirect to employee view on success

#### 5. Delete Employee
- **URL**: `/delete/<employee_id>`
- **Method**: `POST`
- **Description**: Remove employee from directory
- **Response**: Redirect to home page

## Data Models

### Employee Object
```json
{
  "id": "emp-001",
  "fullname": "John Doe",
  "location": "Seattle, WA",
  "job_title": "Software Engineer",
  "badges": ["apple", "coffee", "bug"]
}
```

### Badge System
The application supports various employee badges:

| Badge | Description |
|-------|-------------|
| `apple` | Mac User |
| `windows` | Windows User |
| `linux` | Linux User |
| `video-camera` | Digital Content Star |
| `trophy` | Employee of the Month |
| `camera` | Photographer |
| `plane` | Frequent Flier |
| `paperclip` | Paperclip Afficionado |
| `coffee` | Coffee Snob |
| `gamepad` | Gamer |
| `bug` | Bugfixer |
| `umbrella` | Seattle Fan |

## Form Data

### Add/Edit Employee Form
- **fullname** (required): Employee's full name
- **location** (required): Employee's work location
- **job_title** (required): Employee's job title
- **badges**: Comma-separated list of badge keys

### Example Form Submission
```html
<form method="POST" action="/add">
  <input type="text" name="fullname" value="Jane Smith" required>
  <input type="text" name="location" value="Austin, TX" required>
  <input type="text" name="job_title" value="Product Manager" required>
  <input type="hidden" name="badges" value="trophy,plane,camera">
  <button type="submit">Add Employee</button>
</form>
```

## Error Handling

### Common Error Responses
- **404**: Employee not found
- **500**: Server error or database issue
- **Validation Errors**: Form validation failures

### Error Display
Errors are displayed using Flask's flash message system:
- **Success**: Green notification
- **Error**: Red notification
- **Info**: Blue notification

## Future API Development

### Planned REST API Endpoints
```bash
# Employee Management
GET    /api/employees          # List all employees
POST   /api/employees          # Create new employee
GET    /api/employees/{id}     # Get employee details
PUT    /api/employees/{id}     # Update employee
DELETE /api/employees/{id}     # Delete employee

# Badge Management
GET    /api/badges             # List all badges
POST   /api/badges             # Create new badge
GET    /api/badges/{key}       # Get badge details

# Search and Filtering
GET    /api/employees/search   # Search employees
GET    /api/employees/filter   # Filter by criteria
```

### API Response Format
```json
{
  "success": true,
  "data": {
    "employees": [...],
    "total": 10,
    "page": 1,
    "per_page": 20
  },
  "message": "Employees retrieved successfully"
}
```

## Authentication (Future)

### Planned Authentication Methods
- **API Keys**: Simple key-based authentication
- **JWT Tokens**: JSON Web Token authentication
- **OAuth 2.0**: Third-party authentication
- **Session-based**: Traditional web session authentication

## Rate Limiting (Future)

### Planned Rate Limits
- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Premium**: 10000 requests/hour

## CORS Support (Future)

### Planned CORS Configuration
```python
# Allow cross-origin requests from specified domains
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
```

## Testing the API

### Manual Testing
1. Start the application: `docker compose up -d`
2. Access: http://localhost:8080
3. Test each endpoint manually through the web interface

### Automated Testing (Future)
```bash
# Run API tests
curl -X GET http://localhost:8080/api/employees
curl -X POST http://localhost:8080/api/employees \
  -H "Content-Type: application/json" \
  -d '{"fullname":"Test User","location":"Test City","job_title":"Tester"}'
```

## Integration Examples

### JavaScript Integration
```javascript
// Fetch employees
fetch('/api/employees')
  .then(response => response.json())
  .then(data => {
    console.log('Employees:', data.employees);
  });

// Create employee
fetch('/api/employees', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    fullname: 'New Employee',
    location: 'Remote',
    job_title: 'Developer'
  })
});
```

### Python Integration
```python
import requests

# Get employees
response = requests.get('http://localhost:8080/api/employees')
employees = response.json()

# Create employee
new_employee = {
    'fullname': 'Python User',
    'location': 'Python City',
    'job_title': 'Python Developer'
}
response = requests.post('http://localhost:8080/api/employees', json=new_employee)
```

## Support and Documentation

For additional information:
- [README.md](README.md) - Project overview
- [DEVELOPER.md](DEVELOPER.md) - Development guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide

---

*Note: The current version is primarily a web application. API endpoints are planned for future releases.*