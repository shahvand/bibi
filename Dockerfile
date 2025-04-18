FROM python:3.10-slim

WORKDIR /home/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create directory for static files
RUN mkdir -p /home/app/static /home/app/media

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run entrypoint script
COPY ./entrypoint.sh .
RUN chmod +x /home/app/entrypoint.sh

ENTRYPOINT ["/home/app/entrypoint.sh"] 