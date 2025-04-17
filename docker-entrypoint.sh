#!/bin/bash

set -e

# Wait for MySQL
echo "Waiting for MySQL..."
max_retries=30
count=0
while ! nc -z db 3306 && [ $count -lt $max_retries ]; do
  echo "Waiting for MySQL... (${count}/${max_retries})"
  sleep 2
  count=$((count+1))
done

if [ $count -eq $max_retries ]; then
  echo "Error: Failed to connect to MySQL after ${max_retries} attempts"
  exit 1
fi

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
