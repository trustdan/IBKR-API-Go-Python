FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Create a non-root user to run the application
RUN groupadd -r traderadmin && useradd -r -g traderadmin traderadmin \
    && mkdir -p /app/config \
    && chown -R traderadmin:traderadmin /app

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEALTH_CHECK_PORT=8080

# Expose port for health checks
EXPOSE 8080

# Switch to non-root user
USER traderadmin

# Set read-only filesystem and add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

# Command to run the application
CMD ["python", "-m", "orchestrator.main"]
