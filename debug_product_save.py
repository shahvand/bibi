import os
import sys
import traceback
import django

# تنظیم متغیرهای محیطی
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
os.environ['DATABASE_HOST'] = '192.168.100.26'
os.environ['DATABASE_USER'] = 'root'
os.environ['DATABASE_PASSWORD'] = 'Qpz1zX1'
os.environ['DATABASE_NAME'] = 'bibi'

django.setup()

from workflow.models import Product, Unit
from workflow.forms import ProductForm
from django.db import connection

def debug_database_schema():
    """بررسی ساختار جدول محصول در دیتابیس"""
    cursor = connection.cursor()
    cursor.execute("DESCRIBE workflow_product")
    columns = cursor.fetchall()
    print("ساختار جدول محصول:")
    for column in columns:
        print(f"  {column}")

def test_unit_selection():
    """بررسی واحدهای موجود"""
    print("\nواحدهای موجود:")
    units = Unit.objects.all()
    for unit in units:
        print(f"  ID: {unit.id}, نام: {unit.name}, نماد: {unit.symbol}")
    
    if units.exists():
        default_unit = units.filter(name__icontains='عدد').first() or units.first()
        print(f"واحد پیش‌فرض: ID: {default_unit.id}, نام: {default_unit.name}")
    else:
        print("هیچ واحدی در پایگاه داده وجود ندارد!")

def test_form_save():
    """تست ذخیره محصول با استفاده از فرم"""
    print("\nتست ذخیره با فرم:")
    
    # انتخاب یک واحد
    default_unit = None
    if Unit.objects.exists():
        default_unit = Unit.objects.filter(name__icontains='عدد').first() or Unit.objects.first()
    
    # داده‌های فرم
    form_data = {
        'title': 'محصول تست',
        'code': f'DEBUG-{Product.objects.count() + 1}',
        'description': 'توضیحات تست',
        'price_per_unit': 10000,
    }
    
    # اضافه کردن واحد اگر موجود باشد
    if default_unit:
        form_data['unit_ref'] = default_unit.id
    
    # ایجاد و اعتبارسنجی فرم
    form = ProductForm(data=form_data)
    
    print(f"اعتبارسنجی فرم: {form.is_valid()}")
    if not form.is_valid():
        print("خطاهای فرم:")
        for field, errors in form.errors.items():
            print(f"  {field}: {', '.join(errors)}")
        return
    
    # چاپ داده‌های تمیز شده
    print("داده‌های تمیز شده:")
    for field, value in form.cleaned_data.items():
        print(f"  {field}: {value}")
    
    # ذخیره
    try:
        instance = form.save()
        print(f"محصول با موفقیت ذخیره شد! (ID: {instance.id})")
    except Exception as e:
        print(f"خطا در ذخیره محصول: {type(e).__name__}: {str(e)}")
        traceback.print_exc()

def test_direct_save():
    """تست ذخیره مستقیم محصول بدون استفاده از فرم"""
    print("\nتست ذخیره مستقیم:")
    
    # انتخاب یک واحد
    default_unit = None
    if Unit.objects.exists():
        default_unit = Unit.objects.filter(name__icontains='عدد').first() or Unit.objects.first()
    
    try:
        p = Product(
            title='محصول تست مستقیم',
            code=f'DIRECT-{Product.objects.count() + 1}',
            description='توضیحات تست مستقیم',
            price_per_unit=5000,
            unit='عدد',  # مقدار پیش‌فرض برای فیلد قدیمی
            unit_ref=default_unit  # رابطه با جدول واحدها
        )
        
        # چاپ مقادیر قبل از ذخیره
        print("مقادیر محصول قبل از ذخیره:")
        for field in Product._meta.fields:
            print(f"  {field.name}: {getattr(p, field.name, None)}")
        
        # ذخیره
        p.save()
        print(f"محصول با موفقیت ذخیره شد! (ID: {p.id})")
    except Exception as e:
        print(f"خطا در ذخیره مستقیم: {type(e).__name__}: {str(e)}")
        traceback.print_exc()

def print_product_fields():
    """نمایش فیلدهای مدل محصول"""
    print("\nفیلدهای مدل محصول:")
    for field in Product._meta.fields:
        print(f"  {field.name}: {field.__class__.__name__}")

if __name__ == "__main__":
    print("=== دیباگ محصول ===")
    print("بررسی ساختار دیتابیس...")
    try:
        debug_database_schema()
    except Exception as e:
        print(f"خطا در بررسی ساختار دیتابیس: {str(e)}")
        traceback.print_exc()
    
    print_product_fields()
    test_unit_selection()
    test_form_save()
    test_direct_save()
    
    print("\nاتمام دیباگ") 