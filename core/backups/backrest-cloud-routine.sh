#!/bin/bash
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Local backup first
docker exec -i mastercompose-backrest /backrest.sh --source /source/gitlab --destination "$BACKUP_DIR"

# Upload to S3
docker exec -i mastercompose-backrest /backrest.sh --source "$BACKUP_DIR" --s3-endpoint $BACKREST_S3_ENDPOINT \
    --s3-bucket $BACKREST_S3_BUCKET --s3-key $BACKREST_S3_KEY --s3-secret $BACKREST_S3_SECRET --s3-region $BACKREST_S3_REGION

echo "Backup completed locally and uploaded to S3 at $BACKUP_DIR"
