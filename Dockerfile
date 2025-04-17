FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create app directory
WORKDIR /home/app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gettext \
    pkg-config \
    default-libmysqlclient-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Add Gunicorn
RUN pip install gunicorn

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