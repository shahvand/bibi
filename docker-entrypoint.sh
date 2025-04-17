#!/bin/bash

set -e

# Wait for MySQL
echo "Waiting for MySQL..."
while ! nc -z db 3306; do
  sleep 0.1
done
echo "MySQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if specified in environment variables
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput || true
fi

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn bibi.wsgi:application --bind 0.0.0.0:8000
