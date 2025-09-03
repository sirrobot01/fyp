#!/bin/bash
# setup.sh - Setup script for the Identity Management API

echo "Setting up Identity Management API..."

# Create virtual environment
python -m venv .venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations identity
python manage.py migrate

# Setup OAuth2 demo
echo "Setting up OAuth2 demo application..."
python manage.py setup_oauth_demo

# Create sample data
python manage.py create_samples --users 5

# Setup admin
echo "Setting up admin interface..."
python manage.py setup_admin

# Collect static files
python manage.py collectstatic --noinput

echo "Setup complete!"
echo ""
echo "🚀 Your Identity Management API is ready!"
echo ""
echo "To start the server:"
echo "  1. Activate virtual environment: source identity_env/bin/activate"
echo "  2. Start server: python manage.py runserver"
echo ""
echo "📱 Access Points:"
echo "  • Application: http://127.0.0.1:8000"
echo "  • Admin Panel: http://127.0.0.1:8000/admin"
echo "  • API Docs: http://127.0.0.1:8000/api/v1/"
echo "  • OAuth Demo: http://127.0.0.1:8000/oauth/demo/"
echo ""
echo "🔐 Demo Accounts:"
echo "  • Admin: admin / admin"
echo "  • User: user1 / password123"
echo ""
echo "🔑 OAuth Demo App:"
echo "  • Client ID: demo-client-id"
echo "  • Client Secret: demo-client-secret"
echo ""
echo "Happy coding! 🎉"