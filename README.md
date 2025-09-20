# Identity & Profile Management API

A context-aware digital identity management system that enables users to maintain multiple personas and control data disclosure based on different contexts.

## Overview

This Django-based API addresses the problem of over-disclosure in digital identity systems by implementing context-aware profile management. Users can create different identity profiles for various contexts (legal, social, professional, display, username) and control exactly what information is shared in each scenario.

## Key Features

- **Context-Aware Identity Management**: Multiple identity profiles per user for different contexts
- **HTTP Content Negotiation**: Custom `Accept-Context` header for context-specific data retrieval
- **Field-Level Permissions**: Granular control over individual data fields
- **OAuth 2.0/2.1 Integration**: Secure authorization with scope-based access control
- **GDPR Compliance**: Data minimization through context-based filtering
- **Comprehensive Audit Trail**: Complete logging of data access and modifications
- **Admin Dashboard**: Full administrative interface for user and identity management
- **RESTful API**: Complete REST API with Django REST Framework

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework
- **Database**: SQLite (development), PostgreSQL compatible
- **Authentication**: OAuth 2.0 with django-oauth-toolkit
- **Frontend**: Django templates with Bootstrap styling
- **API Documentation**: Browsable API interface

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Quick Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd fp
```

2. Run the setup script:
```bash
chmod +x start.sh
./start.sh
```

3. Start the development server:
```bash
python manage.py runserver
```

### Manual Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Setup OAuth demo (optional):
```bash
python manage.py setup_oauth_demo
```

6. Create sample data (optional):
```bash
python manage.py create_samples --users 5
```

## Usage

### Access Points

- **Main Application**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin
- **API Documentation**: http://127.0.0.1:8000/api/v1/
- **User Dashboard**: http://127.0.0.1:8000/dashboard/

### API Examples

#### Context-Aware Identity Retrieval

Request user identity with specific context:

```bash
curl -H "Accept-Context: professional" \
     -H "Authorization: Bearer <token>" \
     http://127.0.0.1:8000/api/v1/users/1/identity/
```

#### Available Contexts

- `legal`: Full legal name, verified credentials
- `professional`: Business-appropriate information
- `social`: Casual name, social profiles, bio
- `display`: Preferred display name, avatar
- `username`: Minimal identifier information

#### Creating Identity Profiles

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{
       "context": "professional",
       "given_name": "John",
       "family_name": "Doe",
       "title": "Software Engineer",
       "email": "john.doe@company.com"
     }' \
     http://127.0.0.1:8000/api/v1/identities/
```

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### OAuth 2.0 Setup

The system includes OAuth 2.0 provider functionality. Demo credentials:

- **Client ID**: demo-client-id
- **Client Secret**: demo-client-secret
- **Scopes**: read, write, admin

## Project Structure

```
fp/
├── identity/               # Main application
│   ├── models.py          # Data models
│   ├── views/             # API and web views
│   ├── serializers.py     # REST API serializers
│   ├── permissions.py     # Access control logic
│   └── management/        # Django commands
├── settings/              # Django configuration
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS)
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
└── start.sh             # Setup script
```

## Development

### Running Tests

```bash
python manage.py test
```

### Code Analysis

Generate line count summary:
```bash
cloc . --exclude-dir=.venv,staticfiles > cloc_summary.txt
```

### Management Commands

- `setup_admin`: Create admin user and setup
- `create_samples`: Generate sample users and identities
- `setup_oauth_demo`: Configure OAuth demo application
- `update_oauth_demo`: Update OAuth demo configuration

## Security Features

- **Field-Level Access Control**: Attribute-based access control (ABAC)
- **OAuth 2.0 Scopes**: Granular API access permissions
- **Audit Logging**: Complete access trail with IP and user agent tracking
- **CSRF Protection**: Django CSRF middleware enabled
- **Input Validation**: Comprehensive data validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is developed as part of a university final year project.

## Contact

**Author**: Mukhtar Akere
**Project**: Final Year Project - University of London
**Subject**: Identity & Profile Management API: A Context-Aware Approach to Digital Identity

## Documentation

For detailed technical documentation, architecture decisions, and evaluation results, refer to the project report: `FYP Report.md`