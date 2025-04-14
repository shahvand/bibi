import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # بررسی وجود ستون unit در جدول workflow_product
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'workflow_product' 
        AND COLUMN_NAME = 'unit'
        """
    )
    
    column_exists = cursor.fetchone()[0]
    
    if not column_exists:
        print("Adding 'unit' column to workflow_product table...")
        cursor.execute("ALTER TABLE workflow_product ADD COLUMN unit VARCHAR(20) NULL")
        print("Column added successfully.")
    else:
        print("Column 'unit' already exists in workflow_product table.")

print("Database update completed successfully.") 