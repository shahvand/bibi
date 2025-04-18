FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_DEFAULT_TIMEOUT=300

# Create app directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    pkg-config \
    default-libmysqlclient-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy pip configuration
COPY pip.conf /etc/pip.conf

# Install packages
COPY requirements.txt .
RUN pip install --upgrade pip && \
    for pkg in $(cat requirements.txt); do \
    pip install --prefix=/install $pkg || echo "Failed to install $pkg"; \
done

# Final image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /home/app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    default-mysql-client \
    netcat-openbsd \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages
COPY --from=builder /install /usr/local

# Copy entrypoint script first
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Copy project
COPY . .

# Create static and media directories
RUN mkdir -p /home/app/static
RUN mkdir -p /home/app/media

# Create non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /home/app
USER appuser

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"] 