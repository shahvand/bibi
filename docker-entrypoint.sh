#!/bin/bash

# انتظار برای آماده‌سازی دیتابیس
echo "Waiting for database..."
sleep 10

# اجرای migrations
echo "Applying database migrations..."
python manage.py migrate

# ایجاد کاربر admin
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin_Secure_Pass_2024', 
                                 first_name='مدیر', last_name='سیستم', role='WAREHOUSE_MANAGER')
    print('Superuser created successfully');
else:
    print('Superuser already exists');
"

# جمع‌آوری فایل‌های استاتیک
echo "Collecting static files..."
python manage.py collectstatic --noinput

# اجرای سرور گونیکورن
echo "Starting server..."
gunicorn bibi.wsgi:application --bind 0.0.0.0:8000 --workers 3 