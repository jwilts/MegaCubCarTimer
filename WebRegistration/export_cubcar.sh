#!/bin/bash

# Database credentials
USER="cubcaradmin"
PASSWORD="cubsrock"
HOST="localhost"
DB_NAME="cubcar"

# Backup directory (change as needed)
BACKUP_DIR="//home/jeff/cubcar_webapp/dbase"

# Create the backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate the timestamped filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="cubcar_${TIMESTAMP}.sql"

# Perform the export with mysqldump
mysqldump --user="$USER" --password="$PASSWORD" --host="$HOST" --routines --triggers \
    --databases "$DB_NAME" --add-drop-database --add-drop-table --replace --complete-insert > "$BACKUP_DIR/$FILENAME"

if [ $? -eq 0 ]; then
    echo "Backup successfully created at: $BACKUP_DIR/$FILENAME"
else
    echo "Error: Backup failed!"
    exit 1
fi

