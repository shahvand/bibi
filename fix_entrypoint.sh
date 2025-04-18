#!/bin/bash
# تبدیل فرمت فایل docker-entrypoint.sh از CRLF به LF

# با استفاده از tr، کاراکترهای CR را حذف می‌کنیم
cat docker-entrypoint.sh | tr -d '\r' > docker-entrypoint.tmp
mv docker-entrypoint.tmp docker-entrypoint.sh

# اطمینان از دسترسی اجرایی
chmod +x docker-entrypoint.sh

echo "فرمت فایل docker-entrypoint.sh با موفقیت به LF تبدیل شد." 