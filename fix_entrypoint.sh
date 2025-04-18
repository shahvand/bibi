#!/bin/bash
# تبدیل فرمت فایل docker-entrypoint.sh از CRLF به LF

# با استفاده از tr، کاراکترهای CR را حذف می‌کنیم
cat docker-entrypoint.sh | tr -d '\r' > docker-entrypoint.tmp
mv docker-entrypoint.tmp docker-entrypoint.sh

# اطمینان از دسترسی اجرایی
chmod +x docker-entrypoint.sh

echo "فرمت فایل docker-entrypoint.sh با موفقیت به LF تبدیل شد."

# Create a clean entrypoint.sh file with LF line endings
cat > entrypoint.sh << 'EOL'
#!/bin/bash

# Wait for MySQL to be ready
echo "Waiting for MySQL..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
    sleep 1
done
echo "MySQL started"

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Create superuser if specified in environment variables
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser already exists"
fi

# Start server
echo "Starting server..."
exec gunicorn bibi.wsgi:application --bind 0.0.0.0:8000
EOL

# Make it executable
chmod +x entrypoint.sh

echo "entrypoint.sh has been fixed and made executable." 