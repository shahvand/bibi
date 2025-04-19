@echo off
echo 🧹 پاکسازی کامل کانتینرها و ولوم‌ها...
docker compose down -v

echo 🗑️ حذف تمام ولوم‌ها...
docker volume prune -f

echo 🏗️ ساخت مجدد تصاویر از صفر...
docker compose build --no-cache

echo 🚀 راه‌اندازی کانتینرها...
docker compose up -d

echo ⏳ منتظر راه‌اندازی کامل سیستم...
timeout /t 20

echo ✅ سیستم با موفقیت راه‌اندازی شد!
echo 🌐 برای دسترسی به سیستم به آدرس http://localhost مراجعه کنید.
echo 📝 نام کاربری: admin
echo 🔑 رمز عبور: admin_password

pause 