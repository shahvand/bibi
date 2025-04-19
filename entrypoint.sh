#!/bin/bash

# Set default values for environment variables if not set
DB_HOST=${DATABASE_HOST:-db}
DB_PORT=${DATABASE_PORT:-3306}

# Wait for MySQL to be ready
echo "Waiting for MySQL at $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1
    echo "Still waiting for MySQL..."
done
echo "MySQL started"

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Create superuser if specified in environment variables
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser already exists"
fi

# Start server
echo "Starting server..."
exec gunicorn inventory_management.wsgi:application --bind 0.0.0.0:8000