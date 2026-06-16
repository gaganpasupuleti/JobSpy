# Stage 1: build React frontend (same-origin — no VITE_API_URL needed)
FROM node:20-alpine AS frontend-build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .
ENV VITE_API_URL=
RUN npm run build

# Stage 2: Python API + static frontend
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
COPY backend/scripts/start.sh /app/backend/scripts/start.sh
RUN chmod +x /app/backend/scripts/start.sh
COPY --from=frontend-build /app/dist /app/backend/static

ENV PYTHONPATH=/app:/app/backend
WORKDIR /app/backend

CMD ["/app/backend/scripts/start.sh"]
