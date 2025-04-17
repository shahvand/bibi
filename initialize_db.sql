-- دیتابیس قبلاً توسط docker-entrypoint.sh ایجاد شده است
-- USE bibi_db;

-- جدول کاربران
CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) NOT NULL,
  `branch_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول واحدها
CREATE TABLE IF NOT EXISTS `workflow_unit` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `symbol` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول محصولات
CREATE TABLE IF NOT EXISTS `workflow_product` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `code` varchar(100) NOT NULL,
  `description` text,
  `price_per_unit` decimal(12,0) NOT NULL,
  `current_stock` decimal(10,0) NOT NULL DEFAULT '0',
  `min_stock` decimal(10,0) NOT NULL DEFAULT '0',
  `unit` varchar(20) NOT NULL,
  `unit_ref_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `workflow_product_unit_ref_id` (`unit_ref_id`),
  CONSTRAINT `workflow_product_unit_ref_id_fk` FOREIGN KEY (`unit_ref_id`) REFERENCES `workflow_unit` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول رانندگان
CREATE TABLE IF NOT EXISTS `workflow_driver` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `license_plate` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `notes` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول سفارشات
CREATE TABLE IF NOT EXISTS `workflow_order` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `status` varchar(20) NOT NULL,
  `order_date` datetime(6) NOT NULL,
  `last_edit_time` datetime(6) NOT NULL,
  `approval_date` datetime(6) DEFAULT NULL,
  `delivery_date` datetime(6) DEFAULT NULL,
  `receipt_date` datetime(6) DEFAULT NULL,
  `delivered_at` datetime(6) DEFAULT NULL,
  `notes` text,
  `requester_id` bigint NOT NULL,
  `warehouse_manager_id` bigint DEFAULT NULL,
  `driver_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `workflow_order_requester_id` (`requester_id`),
  KEY `workflow_order_warehouse_manager_id` (`warehouse_manager_id`),
  KEY `workflow_order_driver_id` (`driver_id`),
  CONSTRAINT `workflow_order_requester_id_fk` FOREIGN KEY (`requester_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `workflow_order_warehouse_manager_id_fk` FOREIGN KEY (`warehouse_manager_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `workflow_order_driver_id_fk` FOREIGN KEY (`driver_id`) REFERENCES `workflow_driver` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول آیتم‌های سفارش
CREATE TABLE IF NOT EXISTS `workflow_orderitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `requested_quantity` decimal(10,0) NOT NULL,
  `approved_quantity` decimal(10,0) DEFAULT NULL,
  `price_per_unit` decimal(10,0) DEFAULT NULL,
  `notes` text,
  `order_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `workflow_orderitem_order_id` (`order_id`),
  KEY `workflow_orderitem_product_id` (`product_id`),
  CONSTRAINT `workflow_orderitem_order_id_fk` FOREIGN KEY (`order_id`) REFERENCES `workflow_order` (`id`) ON DELETE CASCADE,
  CONSTRAINT `workflow_orderitem_product_id_fk` FOREIGN KEY (`product_id`) REFERENCES `workflow_product` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- درج داده‌های نمونه - واحدها
INSERT INTO `workflow_unit` (`name`, `symbol`) VALUES
('عدد', 'عدد'),
('کیلوگرم', 'کیلو'),
('متر', 'متر'),
('بسته', 'بسته'),
('جعبه', 'جعبه');

-- درج داده‌های نمونه - کاربر مدیر سیستم
INSERT INTO `auth_user` (`password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`, `branch_name`)
VALUES
('pbkdf2_sha256$600000$Gxa0SzA9Ydj9K33jP7wLNd$M0ZejaXZSj/lpGZnWSuXJvkQ09S4fKTqWjB3YmQhOz4=', NULL, 1, 'admin', 'مدیر', 'سیستم', 'admin@example.com', 1, 1, NOW(), 'ADMIN', NULL);

-- درج داده‌های نمونه - محصولات
INSERT INTO `workflow_product` (`title`, `code`, `description`, `price_per_unit`, `current_stock`, `min_stock`, `unit`, `unit_ref_id`)
VALUES
('موس لاجیتک M180', 'M180', 'موس بی‌سیم لاجیتک مدل M180', 980000, 15, 5, 'عدد', 1),
('کیبورد گیمینگ ایسوس', 'KB-G512', 'کیبورد گیمینگ مکانیکی ایسوس', 2500000, 8, 3, 'عدد', 1),
('مانیتور 24 اینچ سامسونگ', 'SM-24F390', 'مانیتور 24 اینچ سامسونگ با وضوح Full HD', 5800000, 10, 2, 'عدد', 1),
('کابل شبکه Cat6', 'NET-CAT6', 'کابل شبکه Cat6 باکیفیت', 25000, 200, 50, 'متر', 3),
('هارد اکسترنال وسترن دیجیتال 1 ترابایت', 'WD-1T', 'هارد اکسترنال وسترن دیجیتال با ظرفیت 1 ترابایت', 3500000, 12, 3, 'عدد', 1);

-- درج داده‌های نمونه - رانندگان
INSERT INTO `workflow_driver` (`name`, `phone`, `license_plate`, `is_active`, `notes`)
VALUES
('علی محمدی', '09123456789', '12ط345-78', 1, 'راننده اصلی شرکت'),
('حسن رضایی', '09123456788', '45د678-21', 1, 'راننده نیمه وقت'); 