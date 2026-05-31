FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY jobspy /app/jobspy
COPY pyproject.toml /app/pyproject.toml
COPY backend /app/backend
COPY run_worker.py /app/run_worker.py

ENV PYTHONPATH=/app:/app/backend
WORKDIR /app/backend

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
