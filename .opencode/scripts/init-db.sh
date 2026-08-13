#!/usr/bin/env bash
# init-db.sh — Wait until PostgreSQL is ready, then create the app database
# if it does not exist. Intended for the postgres container entrypoint or for
# local dev bootstrap (docker-compose).
#
# Usage:
#   .opencode/scripts/init-db.sh [host] [port] [db] [user] [password]
set -euo pipefail

PGHOST="${1:-postgres}"
PGPORT="${2:-5432}"
PGDB="${3:-app}"
PGUSER="${4:-postgres}"
PGPASSWORD="${5:-postgres}"

export PGPASSWORD

echo "Esperando PostgreSQL en $PGHOST:$PGPORT..."
until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" >/dev/null 2>&1; do
  echo "  postgres aun no esta listo, reintentando en 2s..."
  sleep 2
done
echo "PostgreSQL listo."

if ! psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -tAc \
  "SELECT 1 FROM pg_database WHERE datname = '$PGDB'" | grep -q 1; then
  echo "Creando base de datos '$PGDB'..."
  psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "CREATE DATABASE \"$PGDB\";"
fi
echo "OK: base '$PGDB' disponible."
