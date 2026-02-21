#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."

for i in $(seq 1 30); do
    if python -c "
import sqlalchemy, os
engine = sqlalchemy.create_engine(os.environ['DATABASE_URL'])
engine.connect().close()
" 2>/dev/null; then
        echo "PostgreSQL is ready."
        break
    fi
    sleep 1
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting Vastarion Garage API..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
