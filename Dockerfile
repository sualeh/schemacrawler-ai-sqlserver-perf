# Multi-stage build for optimization
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency specification and install dependencies using Poetry
COPY pyproject.toml ./
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Production stage
FROM python:3.12-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser \
  schemacrawler_ai_sqlserver_perf/ \
  ./schemacrawler_ai_sqlserver_perf/

# Switch to non-root user
USER appuser
RUN ls -lR ./schemacrawler_ai_sqlserver_perf/

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "schemacrawler_ai_sqlserver_perf.main"]
