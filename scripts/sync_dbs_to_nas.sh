#!/usr/bin/env bash
# sync_dbs_to_nas.sh — Copy OpenClaw SQLite databases to NAS for K8s dashboard
# Runs every 15 minutes via crontab on the OpenClaw VM (192.168.1.38)
#
# Crontab entry:
#   */15 * * * * /home/openclaw/.openclaw/scripts/sync_dbs_to_nas.sh >> /home/openclaw/.openclaw/logs/db_sync.log 2>&1
set -euo pipefail

NAS_USER="kazfamily"
NAS_HOST="192.168.1.126"
NAS_PATH="/volume1/data/shared/openclaw-databases"
SSH_KEY="/home/openclaw/.ssh/nas_backup"
DB_DIR="/home/openclaw/.openclaw/data"
BACKUP_DIR="/tmp/clutch_db_snapshots"

# Databases to sync
DATABASES=(
    "cron_log.db"
    "usage_tracking.db"
    "content_ideas.db"
    "knowledge_base.db"
    "job_market.db"
    "youtube_channels.db"
    "briefings.db"
)

echo "$(date '+%Y-%m-%d %H:%M:%S') — Starting DB sync to NAS"

mkdir -p "$BACKUP_DIR"

SYNCED=0
SKIPPED=0
ERRORS=0

for db in "${DATABASES[@]}"; do
    src="$DB_DIR/$db"
    snapshot="$BACKUP_DIR/$db"

    if [ ! -f "$src" ]; then
        echo "  SKIP: $db (not found)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # WAL-safe atomic snapshot using sqlite3 .backup
    if sqlite3 "$src" ".backup '$snapshot'"; then
        # SCP with -O flag for Synology compatibility
        if scp -O -i "$SSH_KEY" -o StrictHostKeyChecking=no "$snapshot" \
            "${NAS_USER}@${NAS_HOST}:${NAS_PATH}/${db}"; then
            echo "  OK: $db"
            SYNCED=$((SYNCED + 1))
        else
            echo "  FAIL: $db (SCP failed)"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo "  FAIL: $db (backup failed)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Clean up snapshots
rm -rf "$BACKUP_DIR"

echo "$(date '+%Y-%m-%d %H:%M:%S') — Done: $SYNCED synced, $SKIPPED skipped, $ERRORS errors"
