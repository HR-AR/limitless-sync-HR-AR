# 🚀 Step-by-Step Setup Guide for HR-AR

## Step 1: Create Your GitHub Repository

1. Go to: https://github.com/new
2. Create a new repository:
   - Repository name: `limitless-notes`
   - Set to **PRIVATE** (important!)
   - Don't initialize with README
   - Click "Create repository"

Your repo will be at: `https://github.com/HR-AR/limitless-notes`

---

## Step 2: Get Your Access Keys

### A. Get Your Limitless API Key
1. Go to Limitless website/app
2. Look for: Settings → API/Developer/Integrations
3. Copy your API key

### B. Get Your GitHub Personal Access Token
1. Go to: https://github.com/settings/tokens/new
2. Give it a name: "Limitless Sync"
3. Set expiration: "No expiration" (or 1 year)
4. Select scopes:
   - ✅ repo (all repo permissions)
5. Click "Generate token"
6. **COPY THE TOKEN NOW** (you won't see it again!)

---

## Step 3: Download and Set Up Files

1. Download the package I created for you
2. Extract the zip file to a folder (e.g., Desktop/limitless-sync)
3. Open Terminal/Command Prompt and navigate to that folder:
   ```bash
   cd Desktop/limitless-sync
   ```

---

## Step 4: Configure Your Credentials

1. Rename `.env.template` to `.env`:
   ```bash
   mv .env.template .env  # Mac/Linux
   ren .env.template .env  # Windows
   ```

2. Edit `.env` file and add your credentials:
   ```
   LIMITLESS_API_KEY=your-limitless-api-key-here
   GITHUB_TOKEN=your-github-token-from-step-2
   GITHUB_USERNAME=HR-AR
   ```

---

## Step 5: Install Python Dependencies

```bash
pip install requests GitPython schedule python-dotenv
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

---

## Step 6: Initialize Git Repository

```bash
# Initialize git in your folder
git init

# Add your GitHub repository as remote
git remote add origin https://github.com/HR-AR/limitless-notes.git

# Create initial commit
git add .
git commit -m "Initial setup"
git branch -M main
git push -u origin main
```

---

## Step 7: Run Your First Bulk Import

Now let's pull ALL your historical data:

```bash
# This will import ALL available data
python bulk_import_limitless.py

# OR start with last 30 days to test
python bulk_import_limitless.py --days-back 30
```

The import will show progress like:
```
Processing 2024-11-25...
  ✓ Saved 2024-11-25 to 2024/11-November/2024-11-25-notes.md
Progress: 1/30 (3%)
```

---

## Step 8: Set Up Automatic Daily Sync

### Option A: GitHub Actions (Recommended - No Computer Needed)

1. Go to your repo: https://github.com/HR-AR/limitless-notes
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add secret:
   - Name: `LIMITLESS_API_KEY`
   - Value: (your Limitless API key)
5. The daily sync will run automatically at 11 PM every day!

### Option B: Run Locally on Your Computer

**Mac:**
```bash
# Add to crontab
crontab -e
# Add this line (runs at 11 PM daily):
0 23 * * * cd /path/to/limitless-sync && python limitless_to_github.py --once
```

**Windows:**
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Limitless Sync"
4. Trigger: Daily at 11 PM
5. Action: Start a program
6. Program: python
7. Arguments: C:\path\to\limitless_to_github.py --once

---

## Step 9: Verify Everything Works

1. Check your GitHub repository: https://github.com/HR-AR/limitless-notes
2. You should see folders like:
   ```
   2024/
     11-November/
       2024-11-25-notes.md
   ```
3. Click on any .md file to see your formatted notes

---

## 🎉 You're Done!

Your Limitless data is now:
- ✅ Backed up to GitHub
- ✅ Organized by date
- ✅ Automatically syncing daily
- ✅ Searchable and version controlled

---

## Quick Reference Commands

```bash
# Import last year of data
python bulk_import_limitless.py --days-back 365

# Import specific dates
python bulk_import_limitless.py --start-date 2024-01-01 --end-date 2024-12-31

# Retry failed imports
python bulk_import_limitless.py --retry-failed

# Manual daily sync
python limitless_to_github.py --once
```
