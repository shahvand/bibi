#!/bin/bash# Wait for PostgreSQL to be readyif [ "$DATABASE_HOST" = "db" ]then    echo "Waiting for PostgreSQL..."        while ! nc -z $DATABASE_HOST $DATABASE_PORT; do        sleep 0.1    done        echo "PostgreSQL started"fi# Apply migrationspython manage.py migrate# Collect static filespython manage.py collectstatic --no-input# Create superuser if specified in environment variablesif [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then    python manage.py createsuperuser --noinput || echo "Superuser already exists"fi# Start serverexec gunicorn bibi.wsgi:application --bind 0.0.0.0:8000 