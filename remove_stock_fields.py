import os
import MySQLdb
import traceback

# تنظیم اطلاعات اتصال به دیتابیس
db_host = os.environ.get('DATABASE_HOST', '192.168.100.26')
db_user = os.environ.get('DATABASE_USER', 'root')
db_password = os.environ.get('DATABASE_PASSWORD', 'Qpz1zX1')
db_name = os.environ.get('DATABASE_NAME', 'bibi')

print(f"تلاش برای اتصال به {db_host}...")

try:
    # اتصال به دیتابیس
    conn = MySQLdb.connect(
        host=db_host,
        user=db_user,
        passwd=db_password,
        db=db_name
    )
    
    print("اتصال با موفقیت برقرار شد.")
    cursor = conn.cursor()
    
    # اجرای دستورات SQL برای حذف ستون‌ها
    print("در حال حذف ستون current_stock...")
    cursor.execute("ALTER TABLE workflow_product DROP COLUMN current_stock")
    
    print("در حال حذف ستون min_stock...")
    cursor.execute("ALTER TABLE workflow_product DROP COLUMN min_stock")
    
    # تایید تغییرات
    conn.commit()
    
    print("عملیات با موفقیت انجام شد!")
    
except Exception as e:
    print(f"خطا: {str(e)}")
    traceback.print_exc()
    
finally:
    # بستن اتصال
    if 'conn' in locals() and conn:
        conn.close()
        print("اتصال به پایگاه داده بسته شد.") 