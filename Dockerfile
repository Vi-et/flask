# Multi-stage Dockerfile for Flask Application

# Stage 1: Builder
FROM python:3.11-slim as builder

# Build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Labels
LABEL maintainer="your-email@example.com" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.version=$VERSION \
      org.label-schema.name="Flask API" \
      org.label-schema.description="Flask REST API with Swagger" \
      org.label-schema.schema-version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 flaskuser && \
    chown -R flaskuser:flaskuser /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/flaskuser/.local

# Copy application code
COPY --chown=flaskuser:flaskuser . .

# Update PATH
ENV PATH=/home/flaskuser/.local/bin:$PATH

# Switch to non-root user
USER flaskuser

# Environment variables
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
