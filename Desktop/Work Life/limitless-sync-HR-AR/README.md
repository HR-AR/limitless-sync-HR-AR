# Limitless Sync - Bulk Import Tool

Automatically sync your Limitless Pendant data to GitHub for permanent storage and easy access.

## Quick Setup

### Step 1: Initial Setup
```bash
# 1. Run the setup script to configure your API keys
./setup_env.sh
```

You'll need:
- **Limitless API Key**: Get from https://my.limitless.ai/api-keys
- **GitHub Personal Access Token**: Create at https://github.com/settings/tokens/new (needs 'repo' scope)
- **GitHub Username**: Your GitHub username (default: HR-AR)

### Step 2: Create GitHub Repository (Optional)
```bash
# This will create the 'limitless-notes' repository if it doesn't exist
./create_github_repo.sh
```

### Step 3: Run Bulk Import
```bash
# Import all historical data (last 365 days)
./run_bulk_import.sh
```

## File Structure

After import, your data will be organized in GitHub like this:
```
limitless-notes/
├── 2024/
│   ├── 01-January/
│   │   ├── 2024-01-01-notes.md
│   │   ├── 2024-01-02-notes.md
│   │   └── ...
│   ├── 02-February/
│   │   └── ...
│   └── ...
├── 2023/
│   └── ...
└── README.md
```

## Manual Commands

### Import Specific Date Range
```bash
source limitless-env/bin/activate
python3 bulk_import_limitless.py --start-date 2024-01-01 --end-date 2024-12-31
```

### Import Last N Days
```bash
source limitless-env/bin/activate
python3 bulk_import_limitless.py --days-back 30
```

### Retry Failed Imports
```bash
source limitless-env/bin/activate
python3 bulk_import_limitless.py --retry-failed
```

## Troubleshooting

### Module Not Found Error
If you get "ModuleNotFoundError", the virtual environment needs to be activated:
```bash
source limitless-env/bin/activate
pip install requests GitPython schedule python-dotenv
```

### API Key Issues
- Make sure your Limitless API key is valid
- Check that your GitHub token has 'repo' permissions
- Run `source .env` to load your configuration

### Rate Limiting
The script automatically handles rate limiting with delays between requests. If you hit limits:
- The script will pause and retry automatically
- Use fewer workers: `--workers 1`
- Use sequential mode: `--sequential`

## Configuration

All settings are stored in `.env` file:
```bash
LIMITLESS_API_KEY='your-limitless-api-key'
GITHUB_TOKEN='your-github-token'
GITHUB_USERNAME='your-username'
```

## Features

- ✅ Bulk import of all historical data
- ✅ Automatic organization by date
- ✅ Parallel processing for faster imports
- ✅ Rate limit handling
- ✅ Resume capability for failed imports
- ✅ Automatic GitHub push
- ✅ Markdown formatting of transcripts

## Next Steps

After bulk import, you can:
1. Set up the continuous sync script to run daily
2. Browse your notes at https://github.com/YOUR_USERNAME/limitless-notes
3. Search through your historical data using GitHub's search

## Support

If you encounter issues:
1. Check the error messages in the terminal
2. Verify your API keys are correct
3. Look for `failed_imports.txt` in the repository folder
4. Try running with `--sequential` flag for more stable processing