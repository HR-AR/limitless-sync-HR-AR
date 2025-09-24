#!/bin/bash
# Setup environment variables for Limitless sync

echo "========================================="
echo "Limitless Sync Environment Setup"
echo "========================================="
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo "Loading existing .env file..."
    source .env
    echo "Current configuration loaded."
    echo ""
fi

# Function to prompt for value with current value display
prompt_with_default() {
    local var_name=$1
    local prompt_text=$2
    local current_value="${!var_name}"

    if [ -n "$current_value" ] && [ "$current_value" != "your-api-key-here" ] && [ "$current_value" != "your-github-token-here" ]; then
        echo "$prompt_text"
        echo "Current value: [hidden for security]"
        echo -n "Press Enter to keep current, or enter new value: "
    else
        echo "$prompt_text"
        echo -n "Enter value: "
    fi

    read new_value

    if [ -n "$new_value" ]; then
        echo "$new_value"
    else
        echo "$current_value"
    fi
}

# Get Limitless API Key
echo "1. LIMITLESS API KEY"
echo "   Get your API key from: https://my.limitless.ai/api-keys"
echo "   (or check your Limitless app settings)"
echo ""
LIMITLESS_API_KEY=$(prompt_with_default LIMITLESS_API_KEY "Limitless API Key:")
echo ""

# Get GitHub Token
echo "2. GITHUB PERSONAL ACCESS TOKEN"
echo "   Create a token at: https://github.com/settings/tokens/new"
echo "   Required scopes: repo (full control of private repositories)"
echo ""
GITHUB_TOKEN=$(prompt_with_default GITHUB_TOKEN "GitHub Personal Access Token:")
echo ""

# Get GitHub Username
echo "3. GITHUB USERNAME"
GITHUB_USERNAME=${GITHUB_USERNAME:-HR-AR}
GITHUB_USERNAME=$(prompt_with_default GITHUB_USERNAME "GitHub Username (default: HR-AR):")
echo ""

# Save to .env file
echo "Saving configuration to .env file..."
cat > .env << EOF
# Limitless Sync Configuration
export LIMITLESS_API_KEY='$LIMITLESS_API_KEY'
export GITHUB_TOKEN='$GITHUB_TOKEN'
export GITHUB_USERNAME='$GITHUB_USERNAME'
EOF

echo "✓ Configuration saved to .env"
echo ""

# Export for current session
export LIMITLESS_API_KEY="$LIMITLESS_API_KEY"
export GITHUB_TOKEN="$GITHUB_TOKEN"
export GITHUB_USERNAME="$GITHUB_USERNAME"

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Your configuration has been saved."
echo ""
echo "To use these settings in future sessions, run:"
echo "  source .env"
echo ""
echo "Ready to run the bulk import? Use:"
echo "  ./run_bulk_import.sh"
echo ""