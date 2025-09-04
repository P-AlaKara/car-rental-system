FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies separately for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port DigitalOcean provides via $PORT
ENV PORT=8080 
EXPOSE 8080

# Default to production config
ENV FLASK_ENV=production \
    PYTHONPATH=/app

# Gunicorn config: 2 workers, 1 thread each, timeout 60s
CMD exec gunicorn --bind 0.0.0.0:"${PORT}" --workers=2 --threads=1 --timeout=60 wsgi:app

