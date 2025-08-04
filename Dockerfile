# Multi-stage Docker build using Builder Pattern
# Stage 1: Builder - Install dependencies and build environment
FROM python:3.12-slim AS builder

# Set environment variables to optimize Python behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org poetry

# Configure Poetry to not create virtual environment (we'll create our own)
ENV POETRY_VENV_IN_PROJECT=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Create and activate virtual environment
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files for building
COPY pyproject.toml ./
COPY README.md ./
COPY schemacrawler_ai_sqlserver_perf/ ./schemacrawler_ai_sqlserver_perf/

# Install dependencies and build the project using Poetry
RUN pip install fastmcp>=0.1.0 \
    && poetry build \
    && pip install dist/*.whl

# Stage 2: Runtime - Create the final lightweight image
FROM python:3.12-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy the virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Set the entry point to run the MCP server
ENTRYPOINT ["python", "-m", "schemacrawler_ai_sqlserver_perf.main"]
