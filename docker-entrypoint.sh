#!/bin/bash

# انتظار برای آماده شدن دیتابیس
echo "Waiting for MySQL..."

# یک تاخیر اولیه برای اطمینان از شروع کامل دیتابیس
sleep 30

# سعی می‌کنیم به دیتابیس متصل شویم
echo "Trying to connect to MySQL..."
attempts=0
while ! mysqladmin ping -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" --silent; do
    attempts=$((attempts+1))
    if [ $attempts -gt 30 ]; then
        echo "Could not connect to MySQL after 30 attempts. Exiting..."
        exit 1
    fi
    echo "Waiting for MySQL to be ready... (attempt $attempts/30)"
    sleep 2
done

echo "MySQL is ready!"

# اجرای مایگریشن‌ها
echo "Applying database migrations..."
python manage.py migrate

# جمع‌آوری فایل‌های استاتیک
echo "Collecting static files..."
python manage.py collectstatic --noinput

# بررسی وجود داده‌های نمونه و ایجاد آنها در صورت لزوم
if [ "$LOAD_SAMPLE_DATA" = "True" ]; then
  echo "Loading sample data..."
  python create_sample_data.py
fi

# اجرای سرور
echo "Starting server..."
exec gunicorn inventory_management.wsgi:application --bind 0.0.0.0:8000 