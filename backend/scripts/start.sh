#!/bin/sh
set -eu

PORT="${PORT:-8000}"
MAX_TRIES="${DB_MIGRATE_RETRIES:-15}"
SLEEP_SEC="${DB_MIGRATE_SLEEP:-3}"

echo "Starting JobBoard API on port ${PORT}..."

i=1
while [ "$i" -le "$MAX_TRIES" ]; do
  if alembic upgrade head; then
    echo "Database migrations complete."
    break
  fi
  echo "Migration attempt ${i}/${MAX_TRIES} failed — retrying in ${SLEEP_SEC}s..."
  i=$((i + 1))
  sleep "$SLEEP_SEC"
done

if [ "$i" -gt "$MAX_TRIES" ]; then
  echo "ERROR: Could not run migrations. Check DATABASE_URL on Railway."
  exit 1
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
