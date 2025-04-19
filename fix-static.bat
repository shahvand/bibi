@echo off
echo 🔍 تشخیص و رفع مشکل فایل‌های استاتیک پنل ادمین...

echo 🛑 توقف موقت کانتینرها...
docker compose stop

echo 🗂️ ایجاد دایرکتوری‌های لازم برای فایل‌های استاتیک...
mkdir static\admin\css 2>NUL
mkdir static\admin\js 2>NUL
mkdir static\admin\img 2>NUL

echo 📋 کپی فایل‌های استاتیک پنل ادمین...
echo این مرحله ممکن است چند دقیقه طول بکشد...

echo 🔄 نصب پکیج django در کانتینر وب...
docker compose exec web pip install django --no-cache-dir

echo 🔍 پیدا کردن مسیر فایل‌های جنگو...
FOR /F "tokens=*" %%g IN ('docker compose exec web pip show django ^| findstr "Location"') do (SET DJANGO_LOCATION=%%g)
set DJANGO_PATH=%DJANGO_LOCATION:~10%

echo 📦 کپی فایل‌های استاتیک ادمین...
docker compose exec web bash -c "cd %DJANGO_PATH%/django/contrib/admin/static && cp -r admin /home/app/web/static/"

echo 👤 تنظیم دسترسی‌های فایل‌ها...
docker compose exec web bash -c "chmod -R 755 /home/app/web/static"

echo 🚀 راه‌اندازی مجدد کانتینرها...
docker compose up -d

echo ⏳ منتظر راه‌اندازی کامل سرویس وب...
timeout /t 15

echo 🔧 اجرای دستی collectstatic...
docker compose exec web python manage.py collectstatic --no-input --clear

echo ✅ فرآیند رفع مشکل فایل‌های استاتیک با موفقیت انجام شد!
echo 🌐 اکنون می‌توانید پنل ادمین را در آدرس http://localhost/admin بررسی کنید.

pause 