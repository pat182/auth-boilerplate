#!/bin/sh
set -e

# Run Alembic migrations
alembic upgrade head

# Start FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload