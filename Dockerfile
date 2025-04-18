FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

# Create directories
RUN mkdir -p $HOME $APP_HOME $HOME/static $HOME/media \
    && mkdir -p $HOME/static/css $HOME/static/js $HOME/static/img \
    && mkdir -p $HOME/media/uploads $HOME/media/products

# Create static files
RUN echo "body { font-family: 'Vazirmatn', 'Tahoma', sans-serif; }" > $HOME/static/css/style.css \
    && echo "body { direction: rtl; text-align: right; }" > $HOME/static/css/rtl.css \
    && echo "// Custom JS for tooltips" > $HOME/static/js/custom.js

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    libcairo2-dev \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR $APP_HOME

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy entrypoint script first and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy project files
COPY . $APP_HOME

# Create a non-root user and set permissions
RUN groupadd -r app && \
    useradd -r -g app app && \
    chown -R app:app $HOME && \
    chown app:app /entrypoint.sh

# Switch to non-root user
USER app

ENTRYPOINT ["/entrypoint.sh"]