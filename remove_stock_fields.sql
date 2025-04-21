-- حذف ستون‌های موجودی از جدول محصولات
ALTER TABLE workflow_product DROP COLUMN current_stock;
ALTER TABLE workflow_product DROP COLUMN min_stock; 