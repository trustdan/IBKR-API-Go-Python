FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the application
RUN groupadd -r traderadmin && useradd -r -g traderadmin traderadmin
RUN mkdir -p /app/config && chown -R traderadmin:traderadmin /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Switch to non-root user
USER traderadmin

# Expose port for health checks
EXPOSE 8080

# Command to run the application
CMD ["python", "-m", "orchestrator.main"]
