#!/usr/bin/env bash
set -euo pipefail
ARCHIVE="$1"
STANDBY_DIR="${2:-/tmp/dr-standby}"
START_NS=$(date +%s%N)

echo "[dr] Verifying backup integrity..."
sha256sum -c "${ARCHIVE}.sha256"

echo "[dr] Restoring SQLite snapshot to standby storage (${STANDBY_DIR})..."
mkdir -p "$STANDBY_DIR"
rm -f "${STANDBY_DIR}/app.db"
tar -xzf "$ARCHIVE" -C "$STANDBY_DIR"
mv "${STANDBY_DIR}"/app-*.db "${STANDBY_DIR}/app.db"

END_NS=$(date +%s%N)
ELAPSED_MS=$(( (END_NS - START_NS) / 1000000 ))
echo "RESTORE_OK target=${STANDBY_DIR}/app.db elapsed_ms=${ELAPSED_MS}"
