#!/bin/bash

echo "🔍 تشخیص و رفع مشکل فایل‌های استاتیک پنل ادمین..."

# توقف کانتینرها بدون حذف ولوم‌ها
echo "🛑 توقف موقت کانتینرها..."
docker compose stop

# کپی فایل‌های ادمین به صورت دستی
echo "🗂️ ایجاد دایرکتوری‌های لازم برای فایل‌های استاتیک..."
mkdir -p static/admin/css
mkdir -p static/admin/js
mkdir -p static/admin/img

# وارد کردن فایل‌های استاتیک پنل ادمین
echo "📋 کپی فایل‌های استاتیک پنل ادمین..."
echo "این مرحله ممکن است چند دقیقه طول بکشد..."

# راه‌اندازی یک کانتینر موقت برای استخراج فایل‌های ادمین
echo "🔄 راه‌اندازی کانتینر موقت برای استخراج فایل‌های ادمین..."
docker run --name temp_django_container -d --rm python:3.11-slim bash -c "pip install django && sleep 3600"

# کپی فایل‌های ادمین از کانتینر موقت
echo "📦 کپی فایل‌های ادمین از کانتینر موقت..."
DJANGO_PATH=$(docker exec temp_django_container pip show django | grep Location | awk '{print $2}')
docker exec temp_django_container bash -c "cd $DJANGO_PATH/django/contrib/admin/static && tar -cf - admin" | tar -xf - -C static/

# حذف کانتینر موقت
echo "🧹 پاکسازی کانتینر موقت..."
docker stop temp_django_container

# تغییر مالکیت فایل‌ها
echo "👤 تنظیم دسترسی‌های فایل‌ها..."
chmod -R 755 static

# راه‌اندازی مجدد کانتینرها
echo "🚀 راه‌اندازی مجدد کانتینرها..."
docker compose up -d

# منتظر شدن برای راه‌اندازی کامل سرویس وب
echo "⏳ منتظر راه‌اندازی کامل سرویس وب..."
sleep 15

# اجرای دستی collectstatic
echo "🔧 اجرای دستی collectstatic..."
docker compose exec web python manage.py collectstatic --no-input --clear

echo "✅ فرآیند رفع مشکل فایل‌های استاتیک با موفقیت انجام شد!"
echo "🌐 اکنون می‌توانید پنل ادمین را در آدرس http://localhost/admin بررسی کنید." 