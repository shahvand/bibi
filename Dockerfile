FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set DNS to Google's for better connectivity
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf
RUN echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# Create app directory
WORKDIR /home/app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gettext \
    pkg-config \
    default-libmysqlclient-dev \
    default-mysql-client \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy pip configuration
COPY pip.conf /etc/pip.conf

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install Django==4.2 mysqlclient==2.2.0 && \
    pip install django-crispy-forms==2.0 crispy-bootstrap4==2022.1 && \
    pip install Pillow==10.0.0 python-dotenv==1.0.0 gunicorn==21.2.0 && \
    pip install django-debug-toolbar==4.2.0 pymemcache==4.0.0 django-filter==23.2 && \
    pip install jdatetime==4.1.1 && \
    pip install pycairo==1.24.0 && \
    pip install WeasyPrint==60.1

# Create static and media directories
RUN mkdir -p /home/app/static
RUN mkdir -p /home/app/media

# Copy entrypoint script first
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Copy project
COPY . .

# Create non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /home/app
USER appuser

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"] 