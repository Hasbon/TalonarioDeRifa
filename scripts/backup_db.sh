#!/usr/bin/env bash
# PostgreSQL backup for Rifa Digital
set -euo pipefail
STAMP=$(date +%Y%m%d_%H%M%S)
OUT_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$OUT_DIR"
FILE="$OUT_DIR/rifa_digital_$STAMP.sql.gz"

docker compose exec -T db pg_dump -U rifa rifa_digital | gzip > "$FILE"
echo "Backup creado: $FILE"
