ALTER TABLE workflow_product MODIFY COLUMN unit_id VARCHAR(20) NOT NULL DEFAULT 'pc';

-- اجرای کوئری برای نمایش اطلاعات جدول بعد از تغییر
DESCRIBE workflow_product;

-- بررسی مایگریشن‌های اعمال نشده
SELECT * FROM django_migrations WHERE app='workflow' ORDER BY id DESC LIMIT 5; 