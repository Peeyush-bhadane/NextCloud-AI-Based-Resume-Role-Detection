#!/usr/bin/env bash
# ==============================================================================
# Nextcloud Automated Backup & Disaster Recovery Script
# College Mini Project: Deployment, Configuration and Management of Nextcloud
# ==============================================================================

set -euo pipefail

BACKUP_ROOT="./backups/$(date +'%Y-%m-%d_%H-%M-%S')"
mkdir -p "$BACKUP_ROOT"

echo "=========================================================="
echo " Starting Nextcloud Cloud Backup at $(date)"
echo " Destination: $BACKUP_ROOT"
echo "=========================================================="

# 1. Enable Nextcloud Maintenance Mode
echo "[1/4] Putting Nextcloud into Maintenance Mode..."
docker exec -u www-data nextcloud-app php occ maintenance:mode --on

# 2. Backup MariaDB Database (mysqldump)
echo "[2/4] Exporting MariaDB Database..."
docker exec nextcloud-db mysqldump -u root -pNextcloudRoot2026! nextcloud > "$BACKUP_ROOT/nextcloud_db.sql"
echo "      Database dump saved to $BACKUP_ROOT/nextcloud_db.sql"

# 3. Archive Nextcloud Configuration & Data
echo "[3/4] Archiving Nextcloud Configuration and Data files..."
docker run --rm \
  --volumes-from nextcloud-app \
  -v "$(pwd)/$BACKUP_ROOT":/backup \
  busybox tar -czf /backup/nextcloud_data.tar.gz /var/www/html/config /var/www/html/data

# 4. Turn off Maintenance Mode
echo "[4/4] Disabling Maintenance Mode..."
docker exec -u www-data nextcloud-app php occ maintenance:mode --off

echo "=========================================================="
echo " Backup Completed Successfully!"
echo " Total Backup Size: $(du -sh "$BACKUP_ROOT" | cut -f1)"
echo "=========================================================="
