#!/bin/bash

# Set the base directory for backups
BACKUP_DIR="/home/jeff/cubcar_backup"

# Set the source directories
NGINX_FILE="/etc/nginx/sites-available/default"
WEBAPP_DIR="/home/jeff/cubcar_webapp"

# Call and wait for the database export to complete
echo "Starting database export..."
./export_cubcar.sh
if [ $? -ne 0 ]; then
    echo "Database export failed. Aborting backup."
    exit 1
fi
echo "Database export completed successfully."

# Create the incremental subfolder in the backup directory
# Find the highest numbered folder and increment
if [ -d "$BACKUP_DIR" ]; then
  LAST_NUM=$(ls -d "$BACKUP_DIR"/*/ 2>/dev/null | awk -F'/' '{print $(NF-1)}' | sort -n | tail -1)
  if [ -z "$LAST_NUM" ]; then
    NEXT_NUM=1
  else
    NEXT_NUM=$((LAST_NUM+1))
  fi
else
  mkdir -p "$BACKUP_DIR"
  NEXT_NUM=1
fi

# Create the new backup folder
NEW_BACKUP="$BACKUP_DIR/$NEXT_NUM"
mkdir -p "$NEW_BACKUP"

# Step 1: Copy the nginx default file to the cubcar_webapp folder
cp "$NGINX_FILE" "$WEBAPP_DIR/"

# Step 2: Copy everything under /home/jeff/cubcar_webapp into the new backup folder
rsync -av --exclude '.venv/' "$WEBAPP_DIR/" "$NEW_BACKUP/"

# Output completion message
echo "Backup complete. Files have been copied to: $NEW_BACKUP"

