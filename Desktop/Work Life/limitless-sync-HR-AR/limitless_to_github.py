#!/usr/bin/env python3
"""
Limitless to GitHub Daily Notes Sync
Pulls transcripts from Limitless API and commits to GitHub with date-based organization
"""

import os
import json
import requests
from datetime import datetime, timedelta
from git import Repo
import schedule
import time
from pathlib import Path

# Configuration
LIMITLESS_API_KEY = os.environ.get('LIMITLESS_API_KEY', 'your-api-key-here')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', 'your-github-token-here')
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'HR-AR')
REPO_NAME = 'limitless-notes'
LOCAL_REPO_PATH = os.path.expanduser(f'~/Documents/{REPO_NAME}')

class LimitlessToGitHub:
    def __init__(self):
        self.base_url = "https://api.limitless.ai/v1"  # Update with actual API endpoint
        self.headers = {
            "Authorization": f"Bearer {LIMITLESS_API_KEY}",
            "Content-Type": "application/json"
        }
        self.setup_repo()
    
    def setup_repo(self):
        """Clone or pull the repository"""
        if not os.path.exists(LOCAL_REPO_PATH):
            print(f"Cloning repository to {LOCAL_REPO_PATH}")
            Repo.clone_from(
                f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git",
                LOCAL_REPO_PATH
            )
        else:
            print("Repository already exists, pulling latest changes")
            self.repo = Repo(LOCAL_REPO_PATH)
            origin = self.repo.remote('origin')
            origin.pull()
    
    def fetch_daily_transcript(self, date=None):
        """Fetch transcript from Limitless API for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Adjust this endpoint based on actual Limitless API documentation
        # This is a template - you'll need to check Limitless docs for exact endpoint
        endpoint = f"{self.base_url}/transcripts"
        params = {
            "date": date,
            "limit": 100  # Adjust based on your needs
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Limitless API: {e}")
            return None
    
    def format_transcript(self, data):
        """Format the transcript data into markdown"""
        date = datetime.now()
        
        # Create markdown content
        content = f"""# Daily Notes - {date.strftime('%B %d, %Y')}

**Date**: {date.strftime('%Y-%m-%d')}  
**Day**: {date.strftime('%A')}  
**Time Generated**: {date.strftime('%I:%M %p')}

---

## Transcript

"""
        
        # Add transcript content (adjust based on actual API response structure)
        if isinstance(data, dict):
            # Example: if API returns conversations/segments
            if 'conversations' in data:
                for idx, conversation in enumerate(data['conversations'], 1):
                    content += f"\n### Conversation {idx}\n"
                    content += f"**Time**: {conversation.get('timestamp', 'N/A')}\n\n"
                    content += f"{conversation.get('text', '')}\n\n"
            elif 'transcript' in data:
                content += data['transcript']
            else:
                # Fallback: just dump the JSON prettily
                content += "```json\n"
                content += json.dumps(data, indent=2)
                content += "\n```"
        else:
            content += str(data)
        
        # Add metadata footer
        content += f"""

---

## Metadata

- **Source**: Limitless Pendant
- **Sync Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **API Version**: v1

---

*This note was automatically generated and synced to GitHub*
"""
        
        return content
    
    def save_and_commit(self, content, date=None):
        """Save content to file and commit to GitHub"""
        if date is None:
            date = datetime.now()
        
        # Create directory structure: year/month/day.md
        year = date.strftime('%Y')
        month = date.strftime('%m-%B')
        day = date.strftime('%d')
        filename = f"{date.strftime('%Y-%m-%d')}-notes.md"
        
        # Create path
        file_path = Path(LOCAL_REPO_PATH) / year / month / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Saved notes to {file_path}")
        
        # Git operations
        try:
            repo = Repo(LOCAL_REPO_PATH)
            
            # Add file
            repo.index.add([str(file_path.relative_to(LOCAL_REPO_PATH))])
            
            # Check if there are changes to commit
            if repo.index.diff("HEAD"):
                # Commit
                commit_message = f"Add daily notes for {date.strftime('%Y-%m-%d')}"
                repo.index.commit(commit_message)
                
                # Push
                origin = repo.remote('origin')
                origin.push()
                
                print(f"Successfully committed and pushed notes for {date.strftime('%Y-%m-%d')}")
            else:
                print("No changes to commit")
                
        except Exception as e:
            print(f"Git error: {e}")
    
    def sync_daily(self):
        """Main sync function to run daily"""
        print(f"\n=== Starting daily sync at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        # Fetch today's transcript
        data = self.fetch_daily_transcript()
        
        if data:
            # Format and save
            content = self.format_transcript(data)
            self.save_and_commit(content)
        else:
            print("No data received from Limitless API")
        
        print("=== Sync complete ===\n")
    
    def sync_historical(self, days_back=7):
        """Sync historical data for the past N days"""
        print(f"Syncing historical data for the past {days_back} days...")
        
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            print(f"Fetching data for {date_str}")
            
            data = self.fetch_daily_transcript(date_str)
            if data:
                content = self.format_transcript(data)
                self.save_and_commit(content, date)
            
            time.sleep(1)  # Be nice to the API

def main():
    """Main execution"""
    import sys
    
    syncer = LimitlessToGitHub()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--historical':
            # Run historical sync
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            print(f"Running historical sync for last {days} days...")
            syncer.sync_historical(days_back=days)
            return
        elif sys.argv[1] == '--once':
            # Run once and exit
            syncer.sync_daily()
            return
    
    # Default: Run once immediately then schedule
    syncer.sync_daily()
    
    # Optional: Sync historical data on first run
    # Uncomment the next line to import last 30 days on first run
    # syncer.sync_historical(days_back=30)
    
    # Schedule daily runs (adjust time as needed)
    schedule.every().day.at("23:00").do(syncer.sync_daily)  # Run at 11 PM daily
    
    print("Scheduler started. Press Ctrl+C to stop.")
    print(f"Next sync scheduled for: {schedule.next_run()}")
    print("\nUsage options:")
    print("  python limitless_to_github.py              # Run continuously")
    print("  python limitless_to_github.py --once       # Run once and exit")
    print("  python limitless_to_github.py --historical [days]  # Import historical data")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
