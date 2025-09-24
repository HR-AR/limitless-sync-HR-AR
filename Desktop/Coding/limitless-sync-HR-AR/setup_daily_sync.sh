#!/bin/bash
# Setup automatic daily sync for Limitless data

echo "========================================="
echo "Setting Up Automatic Daily Sync"
echo "========================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create the daily sync script
cat > "$SCRIPT_DIR/daily_sync.sh" << 'EOF'
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
EOF

chmod +x "$SCRIPT_DIR/daily_sync.sh"

echo "Daily sync script created at: $SCRIPT_DIR/daily_sync.sh"
echo ""

# Set up cron job
echo "Setting up cron job..."
echo ""

# Check if cron job already exists
CRON_CMD="cd \"$SCRIPT_DIR\" && ./daily_sync.sh"
(crontab -l 2>/dev/null | grep -F "$CRON_CMD") > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Cron job already exists"
else
    echo "Choose when to run the daily sync:"
    echo "1) Every day at 2:00 AM"
    echo "2) Every day at 6:00 AM"
    echo "3) Every day at 11:00 PM"
    echo "4) Custom time"
    echo ""
    read -p "Enter choice (1-4): " choice

    case $choice in
        1)
            CRON_TIME="0 2 * * *"
            TIME_DESC="2:00 AM"
            ;;
        2)
            CRON_TIME="0 6 * * *"
            TIME_DESC="6:00 AM"
            ;;
        3)
            CRON_TIME="0 23 * * *"
            TIME_DESC="11:00 PM"
            ;;
        4)
            read -p "Enter hour (0-23): " hour
            read -p "Enter minute (0-59): " minute
            CRON_TIME="$minute $hour * * *"
            TIME_DESC="${hour}:${minute}"
            ;;
        *)
            CRON_TIME="0 2 * * *"
            TIME_DESC="2:00 AM (default)"
            ;;
    esac

    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_TIME $CRON_CMD") | crontab -

    echo "✓ Cron job added to run daily at $TIME_DESC"
fi

echo ""
echo "========================================="
echo "Daily Sync Setup Complete!"
echo "========================================="
echo ""
echo "The sync will run automatically every day."
echo ""
echo "To check cron jobs:     crontab -l"
echo "To edit cron jobs:      crontab -e"
echo "To remove this job:     crontab -l | grep -v 'daily_sync.sh' | crontab -"
echo "To run manually:        ./daily_sync.sh"
echo "To check logs:          tail -f sync_log.txt"
echo ""