#!/bin/bash
# Run bulk import with virtual environment

echo "Starting Limitless bulk import..."
echo "================================="

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "Loading environment configuration..."
    source .env
fi

# Activate virtual environment
source limitless-env/bin/activate

# Check if API key is set
if [ -z "$LIMITLESS_API_KEY" ]; then
    echo "Warning: LIMITLESS_API_KEY not set in environment"
    echo "Please set it with: export LIMITLESS_API_KEY='your-key-here'"
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Warning: GITHUB_TOKEN not set in environment"
    echo "Please set it with: export GITHUB_TOKEN='your-token-here'"
fi

# Run the bulk import for all historical data (365 days by default)
echo ""
echo "Fetching all historical data (last 365 days)..."
python3 bulk_import_limitless.py --days-back 365

echo ""
echo "Import complete!"
echo "Check the output above for details."