FROM python:3.9-slim

WORKDIR /home/app

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# نصب وابستگی‌های سیستمی مورد نیاز
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        pkg-config \
        default-libmysqlclient-dev \
        python3-dev \
        build-essential \
        libpq-dev \
        postgresql-client \
        # وابستگی‌های pycairo
        libcairo2-dev \
        # وابستگی‌های WeasyPrint
        libpango1.0-dev \
        libgdk-pixbuf2.0-dev \
        shared-mime-info \
        libffi-dev \
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

# تنظیم دسترسی به فایل entrypoint
RUN chmod +x docker-entrypoint.sh

# اجرای برنامه
CMD ["./docker-entrypoint.sh"] 