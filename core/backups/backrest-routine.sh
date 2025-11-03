#!/bin/bash
# Set timestamped backup folder
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Run backup from GitLab source data
docker exec -i mastercompose-backrest /backrest.sh --source /source/gitlab --destination "$BACKUP_DIR"

echo "Backup completed at $BACKUP_DIR"
