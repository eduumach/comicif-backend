# Multi-stage build for optimized production image
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency resolution
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv pip install --system --no-deps -r pyproject.toml

# Production stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PORT=8000

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --gid 1000 django \
    && useradd --uid 1000 --gid django --shell /bin/bash --create-home django

# Set work directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project files
COPY --chown=django:django . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R django:django /app

# Switch to non-root user
USER django

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:$PORT/admin/', timeout=10)"

# Start command
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:$PORT --workers 4 config.wsgi:application"]