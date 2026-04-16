#!/bin/sh
set -e

echo "Waiting for database to be ready..."
# Retry up to 10 times with 3s delay
for i in $(seq 1 10); do
  echo "Attempt $i: Running Alembic migrations..."
  if alembic upgrade head; then
    echo "Migrations successful ✅"
    break
  fi
  echo "Attempt $i failed, retrying in 3s..."
  sleep 3
done

echo "Starting Uvicorn on port ${PORT:-8000}..."
# Using exec replaces the shell process with uvicorn for better signal handling
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
