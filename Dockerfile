# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for scientific packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirement.txt ./requirements.txt

# Install Python dependencies with optimizations
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100

# Use BuildKit cache and prefer binary wheels
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install --prefer-binary --no-deps -r requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir pymysql

# Ensure mysql-connector is available too if needed by any code path
RUN pip install --no-cache-dir mysql-connector-python

# Copy application code
COPY . .

# Remove unnecessary files
RUN find . -name "*.pyc" -delete && \
    find . -name "__pycache__" -type d -exec rm -rf {} + || true

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=finance_project.settings \
    PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/ || exit 1

# Run Django with Gunicorn
CMD ["/bin/sh", "-c", "python manage.py migrate --noinput && gunicorn finance_project.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 2 --timeout 120"]