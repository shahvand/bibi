@echo off
echo 🧹 پاکسازی کامل کانتینرها و ولوم‌ها...
docker compose down -v

echo 🗑️ حذف تمام ولوم‌ها...
docker volume prune -f

echo 🔄 اطمینان از تنظیمات استاتیک صحیح...
echo این بخش در ویندوز باید دستی انجام شود. لطفاً تنظیمات entrypoint.sh را چک کنید.

echo 🏗️ ساخت مجدد تصاویر...
docker compose build --no-cache

echo 🚀 راه‌اندازی کانتینرها...
docker compose up -d

echo ⏳ منتظر راه‌اندازی کامل سیستم...
timeout /t 20

echo 🔧 اجرای دستی collectstatic برای اطمینان...
docker compose exec web python manage.py collectstatic --no-input --clear

echo ✅ سیستم با موفقیت راه‌اندازی شد!
echo 🌐 برای دسترسی به سیستم به آدرس http://localhost مراجعه کنید.
echo 📝 نام کاربری: admin
echo 🔑 رمز عبور: admin_password

pause 