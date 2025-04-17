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

# Try to ping MySQL with root user to verify connection
echo "Testing connection to MySQL..."
if ! mysqladmin -h db -u root -p"$MYSQL_ROOT_PASSWORD" ping --silent; then
  echo "Warning: Could not connect to MySQL as root user."
  echo "Trying to continue anyway..."
else
  echo "Connected to MySQL as root user successfully."
  
  # Create user and grant privileges if it doesn't exist
  echo "Ensuring database user exists..."
  mysql -h db -u root -p"$MYSQL_ROOT_PASSWORD" <<EOSQL
    CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;
    CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';
    GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'%';
    FLUSH PRIVILEGES;
EOSQL
  echo "Database setup completed."
fi

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
exec gunicorn inventory_management.wsgi:application --bind 0.0.0.0:8000
