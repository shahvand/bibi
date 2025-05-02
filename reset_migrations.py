import os
import sys
import django
from django.db import connection

# تنظیم تنظیمات جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
django.setup()

# ارتباط با پایگاه داده
with connection.cursor() as cursor:
    # حذف همه مهاجرت‌های workflow
    print("حذف همه مهاجرت‌های workflow...")
    
    cursor.execute(
        "DELETE FROM django_migrations WHERE app = %s",
        ['workflow']
    )
    
    print("همه مهاجرت‌های workflow حذف شدند.")
    
    # نمایش مهاجرت‌های باقی‌مانده
    cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
    migrations = cursor.fetchall()
    
    print("\nمهاجرت‌های باقی‌مانده:")
    for migration in migrations:
        print(f"- {migration[0]}.{migration[1]}")

print("\nعملیات با موفقیت انجام شد. حالا می‌توانید مهاجرت را با --fake-initial اعمال کنید:")
print("python manage.py migrate workflow --fake-initial") 