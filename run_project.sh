#!/bin/bash
# اسکریپت راه‌اندازی کامل پروژه

# تبدیل فرمت فایل docker-entrypoint.sh
./fix_entrypoint.sh

# توقف کانتینرهای فعلی و حذف حجم‌ها
docker compose down -v

# ساخت مجدد تصاویر
docker compose build

# راه‌اندازی کانتینرها در پس‌زمینه
docker compose up -d

# نمایش وضعیت کانتینرها
docker ps

echo "برای مشاهده لاگ‌ها، دستور زیر را اجرا کنید:"
echo "docker compose logs -f" 