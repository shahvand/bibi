#!/bin/bash

# انتظار برای آماده شدن دیتابیس
echo "Waiting for MySQL..."
sleep 10

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