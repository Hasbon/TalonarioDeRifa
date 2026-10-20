#!/usr/bin/env bash
# Restore PostgreSQL backup. Usage: ./scripts/restore_db.sh backups/file.sql.gz
set -euo pipefail
FILE="${1:?Indique el archivo .sql.gz}"
gunzip -c "$FILE" | docker compose exec -T db psql -U rifa -d rifa_digital
echo "Restauración completada desde $FILE"
