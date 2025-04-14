import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # ثبت میگریشن در جدول django_migrations
    cursor.execute(
        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
        ['workflow', '0008_update_product_unit_field']
    )
    
    # اضافه کردن ستون unit_ref_id به جدول product اگر وجود نداشته باشد
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'workflow_product' 
        AND COLUMN_NAME = 'unit_ref_id'
        """
    )
    
    column_exists = cursor.fetchone()[0]
    
    if not column_exists:
        print("Adding unit_ref_id column to workflow_product table...")
        cursor.execute("ALTER TABLE workflow_product ADD COLUMN unit_ref_id BIGINT NULL")
        
        # ایجاد محدودیت کلید خارجی
        cursor.execute(
            """
            ALTER TABLE workflow_product 
            ADD CONSTRAINT fk_product_unit 
            FOREIGN KEY (unit_ref_id) 
            REFERENCES workflow_unit(id) 
            ON DELETE SET NULL
            """
        )
        print("Column added successfully.")
    else:
        print("Column unit_ref_id already exists in workflow_product table.")

print("Database update completed successfully.") 