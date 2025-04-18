#!/bin/bash

echo "🚀 راه‌اندازی سیستم مدیریت انبار..."

# اطمینان از وجود فایل .env
if [ ! -f .env ]; then
  echo "🔄 ساخت فایل .env از نمونه..."
  cp .env.example .env
fi

# اطمینان از وجود دایرکتوری‌های استاتیک
echo "🔄 ساخت دایرکتوری‌های استاتیک..."
mkdir -p static/css static/js static/img
mkdir -p media/uploads media/products

# اطمینان از فرمت LF برای فایل‌های اسکریپت
echo "🔄 تبدیل فرمت فایل entrypoint.sh به LF..."
if command -v dos2unix > /dev/null; then
  dos2unix entrypoint.sh
else
  cat entrypoint.sh | tr -d '\r' > entrypoint.tmp && mv entrypoint.tmp entrypoint.sh
fi
chmod +x entrypoint.sh

# ساخت و اجرای کانتینرها
echo "🔄 متوقف کردن کانتینرهای قبلی..."
docker compose down -v

echo "🔄 ساخت مجدد کانتینرها..."
docker compose build --no-cache

echo "🔄 راه‌اندازی کانتینرها..."
docker compose up -d

echo "✅ سیستم با موفقیت راه‌اندازی شد!"
echo "🌐 برای دسترسی به سیستم به آدرس http://localhost مراجعه کنید."
echo "📝 نام کاربری: admin"
echo "🔑 رمز عبور: admin_password" 