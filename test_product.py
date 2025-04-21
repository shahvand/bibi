import os
import django
import sys

# تنظیم متغیرهای محیطی
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
os.environ['DATABASE_HOST'] = '192.168.100.26'
os.environ['DATABASE_USER'] = 'root'
os.environ['DATABASE_PASSWORD'] = 'Qpz1zX1'
os.environ['DATABASE_NAME'] = 'bibi'

django.setup()

from workflow.models import Product, Unit
from django.db import transaction

def test_product_save():
    """تست ذخیره محصول به‌صورت مستقیم"""
    try:
        # سعی در ذخیره یک محصول جدید
        with transaction.atomic():
            p = Product(
                title='تست محصول جدید',
                code='TEST' + str(Product.objects.count() + 1),
                description='توضیحات تست',
                price_per_unit=1000,
                current_stock=0,
                min_stock=0,
                unit='عدد'
            )
            p.save()
            print(f'محصول با موفقیت ذخیره شد: ID={p.id}')
    except Exception as e:
        print(f'خطا در ذخیره محصول: {type(e).__name__}: {str(e)}')
        import traceback
        traceback.print_exc()

def test_product_form():
    """تست فرم محصول"""
    from workflow.forms import ProductForm
    
    # ایجاد یک فرم با داده‌های معتبر
    form_data = {
        'title': 'تست از طریق فرم',
        'code': 'FORM' + str(Product.objects.count() + 1),
        'description': 'توضیحات تست از طریق فرم',
        'price_per_unit': 2000,
        'unit_ref': None  # می‌توان یک واحد هم انتخاب کرد
    }
    
    try:
        # سعی در ساخت و ذخیره از طریق فرم
        form = ProductForm(data=form_data)
        print(f'آیا فرم معتبر است؟ {form.is_valid()}')
        
        if form.is_valid():
            # نمایش داده‌های تمیز شده
            print('داده‌های تمیز شده فرم:')
            for field, value in form.cleaned_data.items():
                print(f'  {field}: {value}')
            
            # ذخیره
            instance = form.save()
            print(f'محصول از طریق فرم ذخیره شد: ID={instance.id}')
        else:
            # نمایش خطاها
            print('خطاهای فرم:')
            for field, errors in form.errors.items():
                print(f'  {field}: {", ".join(errors)}')
    except Exception as e:
        print(f'خطا در ساخت/ذخیره فرم: {type(e).__name__}: {str(e)}')
        import traceback
        traceback.print_exc()

# اجرای تست‌ها
if __name__ == '__main__':
    print('=== تست ذخیره مستقیم محصول ===')
    test_product_save()
    
    print('\n=== تست فرم محصول ===')
    test_product_form() 