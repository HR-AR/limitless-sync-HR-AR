#!/bin/bash
# Daily sync script for Limitless data

# Change to script directory
cd "$(dirname "$0")"

# Load environment variables
source .env

# Activate virtual environment
source limitless-env/bin/activate

# Get yesterday's date (most recent complete day)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

# Log file
LOG_FILE="sync_log.txt"

echo "$(date): Starting sync for $YESTERDAY" >> $LOG_FILE

# Run the sync
python3 bulk_import_limitless.py --start-date $YESTERDAY --end-date $YESTERDAY >> $LOG_FILE 2>&1

echo "$(date): Sync completed" >> $LOG_FILE
echo "---" >> $LOG_FILE