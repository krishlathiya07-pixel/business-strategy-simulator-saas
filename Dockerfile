FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2 and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Railway provides the PORT environment variable.
# Use a simple shell string for CMD to ensure environment variable expansion.
CMD alembic upgrade head && uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
