FROM python:3.9-slim as builder

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# نصب وابستگی‌های سیستمی مورد نیاز برای بیلد پکیج‌ها
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

# ساخت محیط مجازی و نصب وابستگی‌ها
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# کپی فقط فایل requirements برای کش بهتر
WORKDIR /requirements
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# مرحله نهایی
FROM python:3.9-slim

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# نصب وابستگی‌های زمان اجرا
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# کپی محیط مجازی از مرحله قبل
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# تنظیم دایرکتوری کاری
WORKDIR /home/app

# کپی پروژه
COPY . .

# ایجاد دایرکتوری‌های استاتیک و مدیا
RUN mkdir -p /home/app/static /home/app/media

# تنظیم دسترسی به فایل entrypoint
RUN chmod +x /home/app/docker-entrypoint.sh

# اجرای برنامه
CMD ["/bin/bash", "/home/app/docker-entrypoint.sh"] 