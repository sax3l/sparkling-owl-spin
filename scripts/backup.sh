#!/bin/bash
# This script performs a backup of the PostgreSQL database.
set -e

FILENAME="backup-$(date +%F-%H-%M-%S).sql.gz"
echo "Creating backup $FILENAME..."

pg_dump "$DATABASE_URL" | gzip > "$FILENAME"

# TODO: Add command to upload to S3
# aws s3 cp "$FILENAME" "s3://your-backup-bucket/db_backups/"

echo "Backup complete."
rm "$FILENAME"