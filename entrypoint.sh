#!/bin/bash

# Wait for MySQL to be ready
echo "Waiting for MySQL..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
    sleep 0.1
done
echo "MySQL started"

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Create superuser if specified in environment variables
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py createsuperuser --noinput || echo "Superuser already exists"
fi

# Start server
exec gunicorn bibi.wsgi:application --bind 0.0.0.0:8000