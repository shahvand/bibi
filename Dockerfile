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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Add Gunicorn
RUN pip install gunicorn

# Copy project
COPY . .

# Make entry point executable
RUN chmod +x docker-entrypoint.sh

# Create static and media directories
RUN mkdir -p /home/app/static
RUN mkdir -p /home/app/media

# Create non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /home/app
USER appuser

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"] 