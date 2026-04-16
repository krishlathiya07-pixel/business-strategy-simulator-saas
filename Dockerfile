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

# Copy and make the start script executable
RUN chmod +x start.sh

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Use the start script as the entrypoint
CMD ["/bin/sh", "start.sh"]
