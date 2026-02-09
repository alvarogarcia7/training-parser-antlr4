# Stage 1: Builder
FROM python:3.14-slim AS builder

# Install dependencies: wget for downloads, default-jre-headless for ANTLR, make for build
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    default-jre-headless \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv via pip (already available in Python base image)
RUN python -m pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy project files (build needs README.md)
COPY . .

# Create virtual environment and install dependencies
RUN uv sync --frozen

# Download and compile ANTLR grammar
RUN make compile-grammar

# Stage 2: Runtime
FROM python:3.14-slim

# Create non-root user for running application
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set PATH to use the venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy project files
COPY . .

# Copy compiled grammar from builder
COPY --from=builder /app/dist /app/dist

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Run tests
RUN pytest -v parser tests

# Set entrypoint for parsing
ENTRYPOINT ["python", "main.py"]
