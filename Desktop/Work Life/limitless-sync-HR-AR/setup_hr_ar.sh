#!/bin/bash
# Quick Setup Script for HR-AR's Limitless to GitHub Sync

echo "======================================"
echo "  LIMITLESS → GITHUB SETUP FOR HR-AR"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Let's set up your credentials..."
    echo ""
    
    # Get Limitless API Key
    read -p "Enter your Limitless API Key: " limitless_key
    
    # Get GitHub Token
    echo ""
    echo "Need a GitHub token. Creating one now..."
    echo "Opening GitHub token page in your browser..."
    
    # Try to open browser
    if command -v xdg-open > /dev/null; then
        xdg-open "https://github.com/settings/tokens/new"
    elif command -v open > /dev/null; then
        open "https://github.com/settings/tokens/new"
    else
        echo "Please go to: https://github.com/settings/tokens/new"
    fi
    
    echo ""
    echo "Settings for token:"
    echo "  - Name: 'Limitless Sync'"
    echo "  - Expiration: 'No expiration' or '1 year'"
    echo "  - Scopes: Check 'repo' (all repo permissions)"
    echo ""
    read -p "Enter your GitHub Personal Access Token: " github_token
    
    # Create .env file
    cat > .env << EOF
LIMITLESS_API_KEY=$limitless_key
GITHUB_TOKEN=$github_token
GITHUB_USERNAME=HR-AR
EOF
    
    echo "✓ Created .env file"
else
    echo "✓ .env file already exists"
fi

# Load environment variables
export $(cat .env | grep -v '#' | xargs)

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and run this script again."
    exit 1
fi
echo "✓ Python installed"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install requests GitPython schedule python-dotenv --quiet
echo "✓ Dependencies installed"

# Initialize Git repository
echo ""
echo "Setting up Git repository..."

if [ ! -d .git ]; then
    git init
    git remote add origin https://github.com/HR-AR/limitless-notes.git
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

# Update the repo path in Python scripts
sed -i.bak "s|REPO_NAME = 'limitless-notes'|REPO_NAME = 'limitless-notes'|g" *.py
sed -i.bak "s|GITHUB_USERNAME', 'your-username'|GITHUB_USERNAME', 'HR-AR'|g" *.py

echo ""
echo "======================================"
echo "        SETUP COMPLETE!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Create your GitHub repository:"
echo "   https://github.com/new"
echo "   Name: limitless-notes (PRIVATE!)"
echo ""
echo "2. Run your first import:"
echo "   python3 bulk_import_limitless.py --days-back 30"
echo ""
echo "3. For ALL historical data:"
echo "   python3 bulk_import_limitless.py"
echo ""
echo "======================================"
