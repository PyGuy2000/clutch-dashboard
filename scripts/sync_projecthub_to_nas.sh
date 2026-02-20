#!/usr/bin/env bash
# sync_projecthub_to_nas.sh — Copy ProjectHub SQLite DB to NAS for Clutch dashboard
# Runs every 15 minutes via crontab on WSL
#
# Crontab entry:
#   */15 * * * * /home/robkacz/clutch-dashboard/scripts/sync_projecthub_to_nas.sh >> /home/robkacz/.local/logs/projecthub_sync.log 2>&1
set -euo pipefail

NAS_USER="kazfamily"
NAS_HOST="192.168.1.126"
NAS_PATH="/volume1/data/shared/openclaw-databases"
DB_SRC="/home/robkacz/projects/autoforge_test_app/data/projecthub.db"
BACKUP_DIR="/tmp/projecthub_snapshot"

echo "$(date '+%Y-%m-%d %H:%M:%S') — Starting ProjectHub DB sync to NAS"

if [ ! -f "$DB_SRC" ]; then
    echo "  SKIP: projecthub.db not found at $DB_SRC"
    exit 0
fi

mkdir -p "$BACKUP_DIR"

# WAL-safe atomic snapshot
if python3 -c "
import sqlite3, shutil
conn = sqlite3.connect('$DB_SRC')
backup = sqlite3.connect('$BACKUP_DIR/projecthub.db')
conn.backup(backup)
backup.close()
conn.close()
"; then
    if scp -O "$BACKUP_DIR/projecthub.db" "${NAS_USER}@${NAS_HOST}:${NAS_PATH}/projecthub.db"; then
        echo "  OK: projecthub.db synced"
    else
        echo "  FAIL: SCP failed"
        rm -rf "$BACKUP_DIR"
        exit 1
    fi
else
    echo "  FAIL: backup failed"
    rm -rf "$BACKUP_DIR"
    exit 1
fi

rm -rf "$BACKUP_DIR"
echo "$(date '+%Y-%m-%d %H:%M:%S') — Done"
