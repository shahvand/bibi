#!/usr/bin/env python
import os
import django

# تنظیم محیط جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
django.setup()

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from workflow.models import User, Product, Unit

def add_permissions_to_accountants():
    """اضافه کردن دسترسی‌های مدیریت کالا و واحد به حسابدارها"""
    print("در حال به‌روزرسانی دسترسی‌های کاربران حسابدار...")
    
    # پیدا کردن تمام کاربران با نقش حسابدار
    accountants = User.objects.filter(role='ACCOUNTANT')
    
    if not accountants.exists():
        print("هیچ کاربر حسابداری در سیستم پیدا نشد.")
        return
    
    # دسترسی به مدل Product
    product_content_type = ContentType.objects.get_for_model(Product)
    product_permissions = Permission.objects.filter(content_type=product_content_type)
    
    # دسترسی به مدل Unit
    unit_content_type = ContentType.objects.get_for_model(Unit)
    unit_permissions = Permission.objects.filter(content_type=unit_content_type)
    
    # اضافه کردن دسترسی‌ها به هر حسابدار
    for accountant in accountants:
        print(f"در حال به‌روزرسانی دسترسی‌های کاربر: {accountant.username}")
        
        for perm in product_permissions:
            accountant.user_permissions.add(perm)
            
        for perm in unit_permissions:
            accountant.user_permissions.add(perm)
        
        print(f"دسترسی‌های کاربر {accountant.username} به‌روزرسانی شدند.")
    
    print("تمام دسترسی‌های کاربران حسابدار با موفقیت به‌روزرسانی شدند.")

if __name__ == "__main__":
    add_permissions_to_accountants() 