import os
import sys
import django
from django.db import connection

# تنظیم تنظیمات جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
django.setup()

# ارتباط با پایگاه داده
with connection.cursor() as cursor:
    # حذف مهاجرت‌های مشکل‌دار
    print("حذف مهاجرت‌های مشکل‌دار...")
    
    # حذف مهاجرت‌های خاص که مشکل دارند
    problematic_migrations = [
        'workflow.0006_5_unit_model',
        'workflow.0008_remove_product_stock_fields'
    ]
    
    for migration in problematic_migrations:
        app, name = migration.split('.')
        cursor.execute(
            "DELETE FROM django_migrations WHERE app = %s AND name = %s",
            [app, name]
        )
        print(f"مهاجرت {migration} حذف شد.")
    
    # نمایش مهاجرت‌های باقی‌مانده
    cursor.execute("SELECT app, name FROM django_migrations WHERE app = 'workflow' ORDER BY id")
    migrations = cursor.fetchall()
    
    print("\nمهاجرت‌های باقی‌مانده:")
    for migration in migrations:
        print(f"- {migration[0]}.{migration[1]}")

print("\nعملیات با موفقیت انجام شد. حالا می‌توانید مهاجرت جدید را اعمال کنید:")
print("python manage.py migrate workflow 0012_increase_decimal_digits") 