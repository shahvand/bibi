FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

# Create directory for the app user
RUN mkdir -p $HOME

# Create the appropriate directories
RUN mkdir -p $APP_HOME $HOME/static $HOME/media

# Create a non-root user and set ownership
RUN groupadd -r app && \
    useradd -r -g app app && \
    chown -R app:app $HOME

# Install dependencies (only MySQL related)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    libcairo2-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR $APP_HOME

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . $APP_HOME

# Copy entrypoint and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Change ownership of application files
RUN chown -R app:app $APP_HOME

# Switch to non-root user
USER app

ENTRYPOINT ["/entrypoint.sh"]