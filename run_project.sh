#!/bin/bash
# اسکریپت راه‌اندازی کامل پروژه

echo "🚀 اجرای سیستم مدیریت انبار..."

# اطمینان از وجود static/img
mkdir -p static/img

# ساخت یک favicon ساده اگر وجود نداشته باشد
if [ ! -f static/img/favicon.ico ]; then
    echo "🔄 ساخت فایل favicon.ico..."
    # یک فایل 16x16 پیکسل با رنگ آبی ایجاد می‌کند (می‌توانید با یک فایل واقعی جایگزین کنید)
# ساخت مجدد تصاویر
docker compose build

# راه‌اندازی کانتینرها در پس‌زمینه
docker compose up -d

# نمایش وضعیت کانتینرها
docker ps

echo "برای مشاهده لاگ‌ها، دستور زیر را اجرا کنید:"
echo "docker compose logs -f" 