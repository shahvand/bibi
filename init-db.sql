-- اسکریپت راه‌اندازی اولیه MySQL

-- ساخت دیتابیس اگر وجود نداشته باشد
CREATE DATABASE IF NOT EXISTS bibi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- حذف کاربر در صورت وجود و ساخت مجدد آن
DROP USER IF EXISTS 'bibi_user'@'%';
CREATE USER 'bibi_user'@'%' IDENTIFIED BY 'bibi_password';

-- اعطای دسترسی‌های لازم
GRANT ALL PRIVILEGES ON bibi_db.* TO 'bibi_user'@'%';

-- اعمال تغییرات
FLUSH PRIVILEGES;

-- پیام تأیید
SELECT 'Database and user created successfully' as message; 