# ==============================================================================
# Nextcloud Automated Backup & Disaster Recovery Script (PowerShell / Windows)
# College Mini Project: Deployment, Configuration and Management of Nextcloud
# ==============================================================================

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupDir = Join-Path $PSScriptRoot "backups\$timestamp"

if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting Nextcloud Cloud Backup at $(Get-Date)" -ForegroundColor Cyan
Write-Host " Destination: $backupDir" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Enable Maintenance Mode
Write-Host "[1/4] Putting Nextcloud into Maintenance Mode..." -ForegroundColor Yellow
docker exec -u www-data nextcloud-app php occ maintenance:mode --on

# 2. Backup MariaDB Database (mysqldump)
Write-Host "[2/4] Exporting MariaDB Database..." -ForegroundColor Yellow
$sqlFile = Join-Path $backupDir "nextcloud_db.sql"
docker exec nextcloud-db mysqldump -u root -pNextcloudRoot2026! nextcloud | Out-File -FilePath $sqlFile -Encoding utf8
Write-Host "      Database dump saved to $sqlFile" -ForegroundColor Green

# 3. Archive Nextcloud Configuration & Data
Write-Host "[3/4] Archiving Nextcloud Configuration and Data files..." -ForegroundColor Yellow
$currentDir = (Get-Location).Path -replace '\\', '/'
docker run --rm --volumes-from nextcloud-app -v "${backupDir}:/backup" busybox tar -czf /backup/nextcloud_data.tar.gz /var/www/html/config /var/www/html/data

# 4. Turn off Maintenance Mode
Write-Host "[4/4] Disabling Maintenance Mode..." -ForegroundColor Yellow
docker exec -u www-data nextcloud-app php occ maintenance:mode --off

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Backup Completed Successfully!" -ForegroundColor Green
$backupSize = (Get-ChildItem $backupDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host " Total Backup Size: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
