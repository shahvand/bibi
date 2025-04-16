#!/bin/bash

# انتظار برای آماده شدن دیتابیس
echo "Waiting for MySQL..."

# تابع برای بررسی قابلیت دسترسی دیتابیس
function check_db() {
  python -c "
import sys
import time
import MySQLdb
try:
    MySQLdb.connect(
        host='${DB_HOST}',
        user='${DB_USER}',
        passwd='${DB_PASSWORD}',
        db='${DB_NAME}',
        port=int('${DB_PORT}')
    )
    sys.exit(0)
except Exception as e:
    print(f'Could not connect to database: {e}')
    sys.exit(1)
"
}

# سعی می‌کنیم 20 بار با فاصله 3 ثانیه به دیتابیس متصل شویم
max_attempts=20
counter=0
until check_db || [ $counter -ge $max_attempts ]; do
  echo "Trying to connect to MySQL... ($(($counter+1))/$max_attempts)"
  counter=$((counter+1))
  sleep 3
done

# اگر پس از همه تلاش‌ها هنوز نتوانستیم به دیتابیس متصل شویم، با خطا خارج می‌شویم
if [ $counter -ge $max_attempts ]; then
  echo "Could not connect to MySQL after $max_attempts attempts. Exiting..."
  exit 1
fi

echo "MySQL is up and running!"

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