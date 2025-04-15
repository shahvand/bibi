FROM python:3.10-slim

WORKDIR /app

# نصب پکیج‌های مورد نیاز سیستم
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل‌های پروژه
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# متغیرهای محیطی پایه را تنظیم می‌کنیم
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تنظیم پورت برای اجرای سرور
EXPOSE 8000

# اسکریپت اجرایی برای استارت برنامه
COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"] 