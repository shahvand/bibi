USE bibi_db;

-- اضافه کردن کاربران نمونه با نقش‌های مختلف
-- نام کاربری: branch1 / رمز عبور: Branch1@Secure
INSERT INTO `auth_user` (`password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`, `branch_name`)
VALUES
('pbkdf2_sha256$600000$aqKjCYBHcZFfzLkR2DOxjB$JQF7JiH5veZYBLiZ+jU0t5yFYJ5cxk1CQyKDSlhoGwQ=', NULL, 0, 'branch1', 'شعبه', 'یک', 'branch1@example.com', 0, 1, NOW(), 'REQUESTER', 'شعبه شماره یک');

-- نام کاربری: branch2 / رمز عبور: Branch2@Secure
INSERT INTO `auth_user` (`password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`, `branch_name`)
VALUES
('pbkdf2_sha256$600000$1cLEtxsdnNgXpuLTqW0LGJ$c1G27FXu5Xgpck5Qd0ZcZFiJ83JRm/UlNcEI+G5B8Vs=', NULL, 0, 'branch2', 'شعبه', 'دو', 'branch2@example.com', 0, 1, NOW(), 'REQUESTER', 'شعبه شماره دو');

-- نام کاربری: warehouse / رمز عبور: Warehouse@Secure
INSERT INTO `auth_user` (`password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`, `branch_name`)
VALUES
('pbkdf2_sha256$600000$KJaQd1gveDARXKzXz4Mh2N$e7JfTTfU98ygPQfqJDVqtCX1FpjGsECvFmVPGYX8lB4=', NULL, 0, 'warehouse', 'انباردار', 'اصلی', 'warehouse@example.com', 0, 1, NOW(), 'WAREHOUSE', NULL);

-- نام کاربری: accountant / رمز عبور: Accountant@Secure
INSERT INTO `auth_user` (`password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`, `branch_name`)
VALUES
('pbkdf2_sha256$600000$kIKG8vP2GZnB1WRgjimJ95$WbxnpWjJ1VZOmAIANuT/5gF7nAyPU9XhOZ9vjMXnkms=', NULL, 0, 'accountant', 'حسابدار', 'شرکت', 'accountant@example.com', 0, 1, NOW(), 'ACCOUNTANT', NULL);

-- ایجاد چند سفارش نمونه
INSERT INTO `workflow_order` (`status`, `order_date`, `last_edit_time`, `requester_id`, `warehouse_manager_id`, `driver_id`, `notes`)
VALUES
('PENDING', NOW(), NOW(), 2, NULL, NULL, 'سفارش اولیه از شعبه یک'),
('APPROVED', DATE_SUB(NOW(), INTERVAL 1 DAY), NOW(), 2, 4, 1, 'سفارش تایید شده از شعبه یک'),
('DELIVERED', DATE_SUB(NOW(), INTERVAL 2 DAY), NOW(), 3, 4, 1, 'سفارش تحویل داده شده به شعبه دو');

-- اضافه کردن آیتم‌های سفارش برای سفارش اول (در انتظار)
INSERT INTO `workflow_orderitem` (`order_id`, `product_id`, `requested_quantity`, `approved_quantity`, `price_per_unit`)
VALUES
(1, 1, 2, 2, 980000),  -- دو عدد موس
(1, 3, 1, 1, 5800000); -- یک عدد مانیتور

-- اضافه کردن آیتم‌های سفارش برای سفارش دوم (تایید شده)
INSERT INTO `workflow_orderitem` (`order_id`, `product_id`, `requested_quantity`, `approved_quantity`, `price_per_unit`)
VALUES
(2, 2, 3, 2, 2500000), -- سه عدد کیبورد درخواست شده، دو عدد تایید شده
(2, 4, 50, 50, 25000); -- 50 متر کابل شبکه

-- اضافه کردن آیتم‌های سفارش برای سفارش سوم (تحویل داده شده)
INSERT INTO `workflow_orderitem` (`order_id`, `product_id`, `requested_quantity`, `approved_quantity`, `price_per_unit`)
VALUES
(3, 5, 2, 2, 3500000); -- دو عدد هارد اکسترنال 