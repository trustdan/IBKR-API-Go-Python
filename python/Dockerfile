FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for grpcio
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==2.1.3

# Copy poetry configuration
COPY pyproject.toml poetry.lock* /app/

# Configure poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (without dev dependencies for production)
RUN poetry install --no-interaction --without dev --no-root

# Explicitly ensure grpcio is installed (fallback)
RUN pip install grpcio grpcio-tools

# Copy the rest of the codebase
COPY . /app/

# Set Python path
ENV PYTHONPATH=/app

# Run the application with error logging
CMD ["python", "src/app/main.py"]
