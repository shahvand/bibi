FROM python:3.9-slim

WORKDIR /home/app

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# نصب وابستگی‌های سیستمی مورد نیاز
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل‌های وابستگی و نصب آن‌ها
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# کپی پروژه
COPY . .

# ایجاد دایرکتوری‌های استاتیک و مدیا
RUN mkdir -p /home/app/static /home/app/media

# اجرای collectstatic به صورت خودکار
RUN python manage.py collectstatic --noinput

# اجرای برنامه
CMD ["gunicorn", "bibi.wsgi:application", "--bind", "0.0.0.0:8000"] 