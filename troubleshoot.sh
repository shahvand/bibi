#!/bin/bash
# اسکریپت حل مشکلات رایج

echo "=== بررسی وضعیت کانتینرها ==="
docker ps -a

echo ""
echo "=== بررسی شبکه‌های داکر ==="
docker network ls

echo ""
echo "=== بررسی حجم‌های داکر ==="
docker volume ls

echo ""
echo "=== بررسی وضعیت سرویس MySQL ==="
docker compose exec db mysqladmin -u root -p"$MYSQL_ROOT_PASSWORD" ping || echo "دیتابیس در دسترس نیست"

echo ""
echo "=== بررسی اتصال بین کانتینرها ==="
docker compose exec web ping -c 2 db || echo "اتصال از web به db برقرار نیست"
docker compose exec web ping -c 2 nginx || echo "اتصال از web به nginx برقرار نیست"

echo ""
echo "=== نمایش لاگ‌های خطا ==="
docker compose logs 2>&1 | grep -i error

echo ""
echo "=== حل مشکل CRLF در فایل‌ها ==="
./fix_entrypoint.sh

echo ""
echo "=== پیشنهادات برای حل مشکلات ==="
echo "1. اگر کانتینرها با مشکل مواجه هستند، آنها را ری‌استارت کنید:"
echo "   docker compose restart"
echo ""
echo "2. اگر مشکل حل نشد، پروژه را از نو راه‌اندازی کنید:"
echo "   ./run_project.sh"
echo ""
echo "3. برای دیدن لاگ‌های کامل:"
echo "   ./show_logs.sh" 