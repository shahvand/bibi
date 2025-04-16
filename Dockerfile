FROM python:3.9 as builder

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ساخت محیط مجازی و نصب وابستگی‌ها
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# تنظیم pip برای استفاده از میرور PyPI با تایم‌اوت بالاتر
RUN mkdir -p ~/.pip && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "timeout = 180" >> ~/.pip/pip.conf && \
    echo "index-url = https://pypi.org/simple" >> ~/.pip/pip.conf && \
    echo "trusted-host = pypi.org files.pythonhosted.org" >> ~/.pip/pip.conf && \
    echo "retries = 5" >> ~/.pip/pip.conf

# کپی فقط فایل requirements برای کش بهتر
WORKDIR /requirements
COPY requirements-minimal.txt .

# نصب وابستگی‌ها با استفاده از وابستگی‌های از پیش کامپایل شده
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefer-binary -r requirements-minimal.txt

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