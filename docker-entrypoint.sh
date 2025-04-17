#!/bin/bash

# انتظار برای آماده‌سازی دیتابیس
echo "Waiting for database..."
for i in {1..30}; do
    if mysql -h $DB_HOST -P $DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SELECT 1" >/dev/null 2>&1; then
        echo "Database connection successful!"
        break
    fi
    echo "Waiting for database... attempt $i of 30"
    sleep 5
done

# اجرای اسکریپت‌های SQL در صورتی که فایل LOAD_SAMPLE_DATA=True باشد
if [ "$LOAD_SAMPLE_DATA" = "True" ]; then
    echo "Loading sample data..."
    
    # نصب mysql-client اگر نصب نشده باشد
    apt-get update && apt-get install -y default-mysql-client
    
    echo "Creating database if it doesn't exist..."
    mysql -h $DB_HOST -P $DB_PORT -u$DB_USER -p$DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    
    # اجرای اسکریپت‌های SQL
    echo "Importing initialize_db.sql..."
    mysql -h $DB_HOST -P $DB_PORT -u$DB_USER -p$DB_PASSWORD $DB_NAME < /home/app/initialize_db.sql
    
    echo "Importing add_sample_users.sql..."
    mysql -h $DB_HOST -P $DB_PORT -u$DB_USER -p$DB_PASSWORD $DB_NAME < /home/app/add_sample_users.sql
    
    echo "Sample data loaded successfully!"
else
    # اجرای migrations
    echo "Applying database migrations..."
    python manage.py migrate
    
    # ایجاد کاربر admin
    echo "Creating superuser if needed..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin_Secure_Pass_2024', 
                                 first_name='مدیر', last_name='سیستم', role='WAREHOUSE_MANAGER')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
fi

# جمع‌آوری فایل‌های استاتیک
echo "Collecting static files..."
python manage.py collectstatic --noinput

# اجرای سرور گونیکورن
echo "Starting server..."
gunicorn bibi.wsgi:application --bind 0.0.0.0:8000 --workers 3 