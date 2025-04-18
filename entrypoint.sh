#!/bin/bash

# Wait for postgres to be ready
if [ "$DATABASE_ENGINE" = "django.db.backends.postgresql" ]; then
  echo "Waiting for PostgreSQL..."
  while ! pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER; do
    sleep 0.1
  done
  echo "PostgreSQL started"
fi

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn
exec gunicorn bibi.wsgi:application --bind 0.0.0.0:8000 