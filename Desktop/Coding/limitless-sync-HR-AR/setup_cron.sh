#!/bin/bash
# Setup script to add daily sync to crontab

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CRON_CMD="0 20 * * * cd \"$SCRIPT_DIR\" && ./daily_sync.sh"

echo "========================================="
echo "Setting Up Daily Sync at 8:00 PM"
echo "========================================="
echo ""

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -F "daily_sync.sh") > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Daily sync cron job already exists"
    echo "Updating to 8:00 PM schedule..."
    # Remove old entry and add new one
    (crontab -l 2>/dev/null | grep -v "daily_sync.sh"; echo "$CRON_CMD") | crontab -
else
    echo "Adding new cron job for 8:00 PM daily sync..."
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
fi

echo ""
echo "✓ Cron job set to run daily at 8:00 PM"
echo ""
echo "Current cron jobs:"
crontab -l
echo ""
echo "========================================="
echo "Daily Sync Setup Complete!"
echo "========================================="
echo ""
echo "The sync will run automatically every day at 8:00 PM."
echo "It will pull yesterday's Limitless data and push to GitHub."
echo ""
echo "To test manually:        ./daily_sync.sh"
echo "To view logs:            tail -f sync_log.txt"
echo "To remove cron job:      crontab -l | grep -v 'daily_sync.sh' | crontab -"
echo ""