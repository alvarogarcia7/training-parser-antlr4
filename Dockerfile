# Stage 1: Builder
FROM python:3.14-slim AS builder

# Install dependencies: curl for uv, default-jre-headless for ANTLR, make for build
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    default-jre-headless \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock training.g4 Makefile ./
COPY . .

# Create virtual environment and install dependencies
RUN uv sync --frozen

# Download and compile ANTLR grammar
RUN make compile-grammar

# Stage 2: Runtime
FROM python:3.14-slim

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

# Run tests
RUN pytest -v parser tests

# Set entrypoint for parsing
ENTRYPOINT ["python", "main.py"]
