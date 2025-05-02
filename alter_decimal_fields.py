import os
import sys
import django
from django.db import connection

# تنظیم تنظیمات جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
django.setup()

# ارتباط با پایگاه داده
with connection.cursor() as cursor:
    print("در حال تغییر ساختار جدول‌های پایگاه داده...")
    
    # تغییر ستون price_per_unit در جدول Product
    cursor.execute(
        "ALTER TABLE workflow_product MODIFY COLUMN price_per_unit DECIMAL(15,0) NOT NULL"
    )
    print("ستون price_per_unit در جدول Product به DECIMAL(15,0) تغییر یافت.")
    
    # تغییر ستون‌های مربوط به تعداد و قیمت در جدول OrderItem
    cursor.execute(
        "ALTER TABLE workflow_orderitem MODIFY COLUMN requested_quantity DECIMAL(15,0) NOT NULL"
    )
    print("ستون requested_quantity در جدول OrderItem به DECIMAL(15,0) تغییر یافت.")
    
    cursor.execute(
        "ALTER TABLE workflow_orderitem MODIFY COLUMN approved_quantity DECIMAL(15,0) NULL"
    )
    print("ستون approved_quantity در جدول OrderItem به DECIMAL(15,0) تغییر یافت.")
    
    cursor.execute(
        "ALTER TABLE workflow_orderitem MODIFY COLUMN price_per_unit DECIMAL(15,0) NULL"
    )
    print("ستون price_per_unit در جدول OrderItem به DECIMAL(15,0) تغییر یافت.")

print("\nعملیات با موفقیت انجام شد. حالا می‌توانید تعداد رقم‌های بیشتری وارد کنید.") 