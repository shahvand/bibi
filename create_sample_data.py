import os
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

# تنظیم محیط جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
django.setup()

from workflow.models import User, Product, Driver, Order, OrderItem
from django.utils import timezone

def create_users():
    """ایجاد کاربران نمونه با نقش‌های مختلف"""
    print("ایجاد کاربران...")
    
    # ایجاد کاربران درخواست کننده (شعبه‌ها)
    branches = [
        {'username': 'branch1', 'name': 'شعبه مرکزی', 'email': 'branch1@example.com'},
        {'username': 'branch2', 'name': 'شعبه شمال', 'email': 'branch2@example.com'},
        {'username': 'branch3', 'name': 'شعبه جنوب', 'email': 'branch3@example.com'},
        {'username': 'branch4', 'name': 'شعبه شرق', 'email': 'branch4@example.com'},
        {'username': 'branch5', 'name': 'شعبه غرب', 'email': 'branch5@example.com'},
    ]
    
    requesters = []
    for branch in branches:
        user = User.objects.create_user(
            username=branch['username'],
            email=branch['email'],
            password='password123',
            first_name=branch['name'],
            role='REQUESTER',
            branch_name=branch['name']
        )
        requesters.append(user)
        print(f"کاربر درخواست کننده ایجاد شد: {user.username} ({user.branch_name})")
    
    # ایجاد کاربر انباردار
    warehouse_manager = User.objects.create_user(
        username='warehouse',
        email='warehouse@example.com',
        password='password123',
        first_name='مدیر',
        last_name='انبار',
        role='WAREHOUSE'
    )
    print(f"کاربر انباردار ایجاد شد: {warehouse_manager.username}")
    
    # ایجاد کاربر حسابدار
    accountant = User.objects.create_user(
        username='accountant',
        email='accountant@example.com',
        password='password123',
        first_name='حسابدار',
        last_name='سیستم',
        role='ACCOUNTANT'
    )
    print(f"کاربر حسابدار ایجاد شد: {accountant.username}")
    
    return requesters, warehouse_manager, accountant

def create_products():
    """ایجاد محصولات نمونه"""
    print("\nایجاد محصولات...")
    
    products = [
        {'title': 'برنج ایرانی', 'code': 'R001', 'unit': 'کیلوگرم', 'price_per_unit': Decimal('150000')},
        {'title': 'روغن مایع', 'code': 'O001', 'unit': 'لیتر', 'price_per_unit': Decimal('120000')},
        {'title': 'قند', 'code': 'S001', 'unit': 'کیلوگرم', 'price_per_unit': Decimal('80000')},
        {'title': 'چای', 'code': 'T001', 'unit': 'بسته', 'price_per_unit': Decimal('200000')},
        {'title': 'ماکارونی', 'code': 'P001', 'unit': 'بسته', 'price_per_unit': Decimal('40000')},
        {'title': 'رب گوجه', 'code': 'TP001', 'unit': 'قوطی', 'price_per_unit': Decimal('65000')},
        {'title': 'حبوبات', 'code': 'B001', 'unit': 'کیلوگرم', 'price_per_unit': Decimal('90000')},
        {'title': 'نوشابه', 'code': 'SD001', 'unit': 'بطری', 'price_per_unit': Decimal('15000')},
        {'title': 'آب معدنی', 'code': 'W001', 'unit': 'بطری', 'price_per_unit': Decimal('8000')},
        {'title': 'شکر', 'code': 'SG001', 'unit': 'کیلوگرم', 'price_per_unit': Decimal('70000')},
    ]
    
    product_objects = []
    for p in products:
        product = Product.objects.create(
            title=p['title'],
            code=p['code'],
            unit=p['unit'],
            price_per_unit=p['price_per_unit']
        )
        product_objects.append(product)
        print(f"محصول ایجاد شد: {product.title} ({product.code})")
    
    return product_objects

def create_drivers():
    """ایجاد رانندگان نمونه"""
    print("\nایجاد رانندگان...")
    
    drivers = [
        {'name': 'علی محمدی', 'phone': '09123456789'},
        {'name': 'رضا احمدی', 'phone': '09123456788'},
        {'name': 'حسن کریمی', 'phone': '09123456787'},
        {'name': 'مهدی رضایی', 'phone': '09123456786'},
        {'name': 'جواد صادقی', 'phone': '09123456785'},
    ]
    
    driver_objects = []
    for d in drivers:
        driver = Driver.objects.create(
            name=d['name'],
            phone=d['phone'],
            is_active=True
        )
        driver_objects.append(driver)
        print(f"راننده ایجاد شد: {driver.name}")
    
    return driver_objects

def create_orders(requesters, warehouse_manager, products, drivers):
    """ایجاد سفارش‌های نمونه"""
    print("\nایجاد سفارش‌ها...")
    
    # تاریخ‌های مختلف برای سفارش‌ها
    now = timezone.now()
    dates = [
        now - timedelta(days=10),  # 10 روز قبل
        now - timedelta(days=7),   # 7 روز قبل
        now - timedelta(days=5),   # 5 روز قبل
        now - timedelta(days=3),   # 3 روز قبل
        now - timedelta(days=1),   # 1 روز قبل
        now,                       # امروز
    ]
    
    # ایجاد 20 سفارش نمونه
    for i in range(1, 21):
        # انتخاب تصادفی درخواست کننده
        requester = random.choice(requesters)
        
        # انتخاب تصادفی تاریخ
        order_date = random.choice(dates)
        
        # تعیین وضعیت سفارش
        status_choice = random.randint(1, 5)
        if status_choice == 1:
            status = 'PENDING'
            approval_date = None
            delivery_date = None
            receipt_date = None
            driver = None
        elif status_choice == 2:
            status = 'APPROVED'
            approval_date = order_date + timedelta(hours=random.randint(1, 24))
            delivery_date = None
            receipt_date = None
            driver = None
        elif status_choice == 3:
            status = 'REJECTED'
            approval_date = order_date + timedelta(hours=random.randint(1, 24))
            delivery_date = None
            receipt_date = None
            driver = None
        elif status_choice == 4:
            status = 'DELIVERED'
            approval_date = order_date + timedelta(hours=random.randint(1, 24))
            delivery_date = approval_date + timedelta(hours=random.randint(1, 48))
            receipt_date = None
            driver = random.choice(drivers)
        else:
            status = 'RECEIVED'
            approval_date = order_date + timedelta(hours=random.randint(1, 24))
            delivery_date = approval_date + timedelta(hours=random.randint(1, 48))
            receipt_date = delivery_date + timedelta(hours=random.randint(1, 24))
            driver = random.choice(drivers)
        
        # ایجاد سفارش
        order = Order.objects.create(
            requester=requester,
            warehouse_manager=warehouse_manager if status != 'PENDING' else None,
            driver=driver,
            status=status,
            order_date=order_date,
            approval_date=approval_date,
            delivery_date=delivery_date,
            receipt_date=receipt_date,
            notes=f"سفارش نمونه شماره {i}" if random.choice([True, False]) else ""
        )
        
        # ایجاد اقلام سفارش (بین 1 تا 5 قلم)
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, num_items)
        
        for product in selected_products:
            requested_quantity = Decimal(str(random.randint(1, 10)))
            
            if status == 'PENDING':
                approved_quantity = None
                price_per_unit = None
            else:
                # گاهی اوقات مقدار تأیید شده با مقدار درخواستی متفاوت است
                approved_quantity = requested_quantity
                if random.choice([True, False, False]):  # احتمال 1/3
                    adjustment = Decimal(str(random.randint(-2, 2)))
                    approved_quantity = max(Decimal('0.1'), requested_quantity + adjustment)
                
                price_per_unit = product.price_per_unit
                # گاهی اوقات قیمت تغییر می‌کند
                if random.choice([True, False, False]):  # احتمال 1/3
                    price_adjustment = random.uniform(-0.1, 0.1)  # تغییر قیمت تا 10 درصد
                    price_per_unit = price_per_unit * (1 + Decimal(str(price_adjustment)))
            
            OrderItem.objects.create(
                order=order,
                product=product,
                requested_quantity=requested_quantity,
                approved_quantity=approved_quantity,
                price_per_unit=price_per_unit,
                notes="" if random.choice([True, True, False]) else "توضیحات نمونه برای این آیتم"
            )
        
        print(f"سفارش ایجاد شد: شماره {order.id} - وضعیت: {status} - تعداد اقلام: {num_items}")

def main():
    """تابع اصلی برای اجرای همه فرآیندهای ایجاد داده"""
    print("=" * 50)
    print("شروع ایجاد داده‌های نمونه برای سیستم مدیریت انبار")
    print("=" * 50)
    
    # حذف داده‌های موجود از مدل‌ها (به غیر از کاربر مدیر)
    print("\nحذف داده‌های قبلی...")
    User.objects.filter(is_superuser=False).delete()
    Product.objects.all().delete()
    Driver.objects.all().delete()
    Order.objects.all().delete()
    OrderItem.objects.all().delete()
    
    # ایجاد داده‌های نمونه
    requesters, warehouse_manager, accountant = create_users()
    products = create_products()
    drivers = create_drivers()
    create_orders(requesters, warehouse_manager, products, drivers)
    
    print("\n" + "=" * 50)
    print("داده‌های نمونه با موفقیت ایجاد شدند!")
    print("=" * 50)
    print("\nاطلاعات ورود به سیستم:")
    print("کاربران درخواست کننده (شعبه‌ها): نام کاربری: branch1 تا branch5، رمز عبور: password123")
    print("کاربر انباردار: نام کاربری: warehouse، رمز عبور: password123")
    print("کاربر حسابدار: نام کاربری: accountant، رمز عبور: password123")
    print("کاربر مدیر: نام کاربری: admin، رمز عبور: (رمزی که هنگام ایجاد مدیر وارد کردید)")

if __name__ == "__main__":
    main() 