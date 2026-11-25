#!/usr/bin/env bash
set -euo pipefail
DB_FILE="${1:-/tmp/dr-primary/app.db}"
BACKUP_DIR="${2:-/tmp/dr-backups}"
mkdir -p "$BACKUP_DIR"
TS=$(date -u +%Y%m%dT%H%M%SZ)
SNAP="${BACKUP_DIR}/app-${TS}.db"
ARCHIVE="${BACKUP_DIR}/backup-${TS}.tar.gz"

python3 -c "import sqlite3; s=sqlite3.connect('${DB_FILE}'); d=sqlite3.connect('${SNAP}'); s.backup(d); d.close(); s.close()"
tar -czf "$ARCHIVE" -C "$BACKUP_DIR" "$(basename "$SNAP")"
sha256sum "$ARCHIVE" > "${ARCHIVE}.sha256"
rm -f "$SNAP"
echo "BACKUP_OK archive=${ARCHIVE} sha256=$(awk '{print $1}' "${ARCHIVE}.sha256")"
