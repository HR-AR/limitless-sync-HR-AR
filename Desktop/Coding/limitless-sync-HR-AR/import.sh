#!/bin/bash

# Limitless Bulk Import Runner
# Easy commands for importing your Limitless data

echo "========================================"
echo "    LIMITLESS BULK IMPORT TOOL"
echo "========================================"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
else
    echo "Warning: .env file not found!"
    echo "Please create .env from .env.template first"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Menu
echo "Select an import option:"
echo ""
echo "1) Import LAST 30 DAYS"
echo "2) Import LAST 90 DAYS"
echo "3) Import LAST 365 DAYS (Full Year)"
echo "4) Import ALL AVAILABLE DATA"
echo "5) Import CUSTOM DATE RANGE"
echo "6) Retry FAILED imports"
echo "7) Quick import (Last 7 days)"
echo ""
read -p "Enter choice [1-7]: " choice

case $choice in
    1)
        echo "Importing last 30 days..."
        python3 bulk_import_limitless.py --days-back 30
        ;;
    2)
        echo "Importing last 90 days..."
        python3 bulk_import_limitless.py --days-back 90
        ;;
    3)
        echo "Importing last 365 days..."
        python3 bulk_import_limitless.py --days-back 365
        ;;
    4)
        echo "Importing all available data..."
        echo "This may take a while depending on how much data you have."
        read -p "Continue? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            python3 bulk_import_limitless.py
        fi
        ;;
    5)
        read -p "Enter start date (YYYY-MM-DD): " start_date
        read -p "Enter end date (YYYY-MM-DD) or press Enter for today: " end_date
        if [ -z "$end_date" ]; then
            python3 bulk_import_limitless.py --start-date "$start_date"
        else
            python3 bulk_import_limitless.py --start-date "$start_date" --end-date "$end_date"
        fi
        ;;
    6)
        echo "Retrying failed imports..."
        python3 bulk_import_limitless.py --retry-failed
        ;;
    7)
        echo "Quick import - last 7 days..."
        python3 bulk_import_limitless.py --days-back 7 --workers 1
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Import process complete!"
echo "Check your GitHub repository for the imported notes."
echo "========================================"
