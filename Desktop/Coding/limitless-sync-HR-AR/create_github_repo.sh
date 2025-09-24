#!/bin/bash
# Create GitHub repository if it doesn't exist

echo "Checking/Creating GitHub Repository..."
echo "======================================"

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found. Run ./setup_env.sh first"
    exit 1
fi

# Check if repo exists
echo "Checking if repository 'limitless-notes' exists..."
REPO_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_USERNAME/limitless-notes")

if [ "$REPO_EXISTS" = "200" ]; then
    echo "✓ Repository already exists"
else
    echo "Repository doesn't exist. Creating..."

    # Create the repository
    curl -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "limitless-notes",
            "description": "Personal notes and transcripts from Limitless Pendant",
            "private": false,
            "auto_init": true
        }' \
        "https://api.github.com/user/repos"

    echo ""
    echo "✓ Repository created successfully"
fi

echo ""
echo "Repository URL: https://github.com/$GITHUB_USERNAME/limitless-notes"
echo ""