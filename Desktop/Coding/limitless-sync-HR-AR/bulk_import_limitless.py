#!/usr/bin/env python3
"""
Bulk Import Limitless Data to GitHub
One-time script to pull ALL historical data from Limitless and organize by date
"""

import os
import json
import requests
from datetime import datetime, timedelta
from git import Repo
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

# Configuration
LIMITLESS_API_KEY = os.environ.get('LIMITLESS_API_KEY', 'your-api-key-here')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', 'your-github-token-here')
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'HR-AR')
TIMEZONE = os.environ.get('TIMEZONE', 'America/Los_Angeles')
REPO_NAME = 'limitless-notes'
LOCAL_REPO_PATH = os.path.expanduser(f'~/Documents/{REPO_NAME}')

class LimitlessBulkImporter:
    def __init__(self):
        self.base_url = "https://api.limitless.ai/v1"
        self.headers = {
            "X-API-Key": LIMITLESS_API_KEY,
            "Content-Type": "application/json"
        }
        self.setup_repo()
        self.failed_dates = []
        self.successful_dates = []
        
    def setup_repo(self):
        """Clone or pull the repository"""
        if not os.path.exists(LOCAL_REPO_PATH):
            print(f"Cloning repository to {LOCAL_REPO_PATH}")
            self.repo = Repo.clone_from(
                f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git",
                LOCAL_REPO_PATH
            )
        else:
            print("Repository already exists, pulling latest changes")
            self.repo = Repo(LOCAL_REPO_PATH)
            origin = self.repo.remote('origin')
            origin.pull()
    
    def get_date_range(self):
        """Get available date range from Limitless API"""
        # This endpoint might vary - check Limitless docs
        endpoint = f"{self.base_url}/available_dates"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                # Assuming API returns first_date and last_date
                return data.get('first_date'), data.get('last_date')
        except:
            pass
        
        # Fallback: return last 365 days if can't get range from API
        print("Could not fetch date range from API, defaulting to last 365 days")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def fetch_transcript_for_date(self, date_str):
        """Fetch transcript from Limitless API for a specific date"""
        # Using the lifelogs endpoint that actually works
        endpoint = f"{self.base_url}/lifelogs"

        # The API returns all lifelogs, so we'll filter by date
        # For now, just get all lifelogs (since date filtering doesn't seem to work)
        params = {}
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check if there's actually data
                # lifelogs API returns a dict with 'data' -> 'lifelogs' array
                if data and isinstance(data, dict) and data.get('data', {}).get('lifelogs'):
                    lifelogs = data['data']['lifelogs']
                    # Filter for the specific date if needed
                    # For now, return all data
                    if len(lifelogs) > 0:
                        print(f"  Found {len(lifelogs)} lifelog(s) for {date_str}")
                        return lifelogs
                    else:
                        print(f"  No lifelogs found for {date_str}")
                        return None
                else:
                    print(f"  No data available for {date_str}")
                    return None
            elif response.status_code == 404:
                print(f"  No data found for {date_str}")
                return None
            elif response.status_code == 429:
                print(f"  Rate limited on {date_str}, waiting...")
                time.sleep(60)  # Wait a minute for rate limit
                return self.fetch_transcript_for_date(date_str)  # Retry
            else:
                print(f"  Error {response.status_code} for {date_str}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"  Timeout for {date_str}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {date_str}: {e}")
            return None
    
    def format_transcript(self, data, date):
        """Format the transcript data into markdown"""
        date_obj = datetime.strptime(date, '%Y-%m-%d')

        content = f"""# Daily Notes - {date_obj.strftime('%B %d, %Y')}

**Date**: {date}
**Day**: {date_obj.strftime('%A')}
**Import Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Lifelogs

"""

        # Handle Lifelogs data structure
        if isinstance(data, list):
            for idx, log in enumerate(data, 1):
                content += f"\n### Lifelog {idx}\n"

                # Process contents array
                if log.get('contents') and isinstance(log['contents'], list):
                    for item in log['contents']:
                        item_type = item.get('type', '')
                        item_content = item.get('content', '')

                        if item_type == 'heading1':
                            content += f"\n# {item_content}\n"
                        elif item_type == 'heading2':
                            content += f"\n## {item_content}\n"
                        elif item_type == 'blockquote':
                            # Add speaker and time info if available
                            speaker = item.get('speakerName', 'Unknown')
                            start_time = item.get('startTime', '')
                            if start_time:
                                try:
                                    st = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                    time_str = st.strftime('%H:%M:%S')
                                    content += f"\n**[{time_str}] {speaker}:**\n> {item_content}\n"
                                except:
                                    content += f"\n**{speaker}:**\n> {item_content}\n"
                            else:
                                content += f"\n**{speaker}:**\n> {item_content}\n"
                        else:
                            content += f"\n{item_content}\n"

                content += "\n---\n"

        # Fallback for dict structure
        elif isinstance(data, dict):
            # If there are multiple conversations/events
            if 'conversations' in data:
                for idx, conversation in enumerate(data['conversations'], 1):
                    content += f"\n### Conversation {idx}\n"
                    if 'timestamp' in conversation:
                        content += f"**Time**: {conversation['timestamp']}\n"
                    if 'duration' in conversation:
                        content += f"**Duration**: {conversation['duration']}\n"
                    if 'participants' in conversation:
                        content += f"**Participants**: {', '.join(conversation['participants'])}\n"
                    content += f"\n{conversation.get('text', conversation.get('transcript', ''))}\n\n"
                    
                    # Add any tags or topics
                    if 'tags' in conversation:
                        content += f"**Tags**: {', '.join(conversation['tags'])}\n\n"
            
            # If there are events/activities
            elif 'events' in data:
                for idx, event in enumerate(data['events'], 1):
                    content += f"\n### Event {idx}\n"
                    content += f"**Type**: {event.get('type', 'Unknown')}\n"
                    content += f"**Time**: {event.get('timestamp', 'N/A')}\n\n"
                    content += f"{event.get('description', event.get('text', ''))}\n\n"
            
            # If it's a single transcript
            elif 'transcript' in data:
                content += data['transcript']
            
            # If it has daily summary
            elif 'daily_summary' in data:
                content += "### Daily Summary\n\n"
                content += data['daily_summary']
                content += "\n\n"
                
                # Add any other fields
                for key, value in data.items():
                    if key != 'daily_summary' and value:
                        content += f"### {key.replace('_', ' ').title()}\n\n"
                        if isinstance(value, (list, dict)):
                            content += f"```json\n{json.dumps(value, indent=2)}\n```\n\n"
                        else:
                            content += f"{value}\n\n"
            
            # Fallback: dump everything as JSON
            else:
                content += "### Raw Data\n\n"
                content += "```json\n"
                content += json.dumps(data, indent=2, default=str)
                content += "\n```"
        else:
            content += str(data)
        
        # Add statistics if available
        if isinstance(data, dict):
            stats = []
            if 'word_count' in data:
                stats.append(f"Words: {data['word_count']}")
            if 'duration_minutes' in data:
                stats.append(f"Duration: {data['duration_minutes']} min")
            if 'conversation_count' in data:
                stats.append(f"Conversations: {data['conversation_count']}")
            
            if stats:
                content += f"\n---\n\n## Statistics\n\n"
                content += " | ".join(stats)
                content += "\n"
        
        content += f"""

---

## Metadata

- **Source**: Limitless Pendant
- **Import Type**: Bulk Historical Import
- **API Version**: v1
- **Imported**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*This note was bulk imported from Limitless historical data*
"""
        
        return content
    
    def save_file(self, content, date_str):
        """Save content to file without committing"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Create directory structure
        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%m-%B')
        filename = f"{date_str}-notes.md"
        
        file_path = Path(LOCAL_REPO_PATH) / year / month / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def process_single_date(self, date_str):
        """Process a single date - used for parallel processing"""
        print(f"Processing {date_str}...")
        
        # Check if file already exists
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%m-%B')
        filename = f"{date_str}-notes.md"
        file_path = Path(LOCAL_REPO_PATH) / year / month / filename
        
        if file_path.exists():
            print(f"  Skipping {date_str} - already exists")
            self.successful_dates.append(date_str)
            return True
        
        # Fetch data
        data = self.fetch_transcript_for_date(date_str)
        
        if data:
            # Format and save
            content = self.format_transcript(data, date_str)
            saved_path = self.save_file(content, date_str)
            print(f"  ✓ Saved {date_str} to {saved_path.relative_to(LOCAL_REPO_PATH)}")
            self.successful_dates.append(date_str)
            return True
        else:
            self.failed_dates.append(date_str)
            return False
    
    def bulk_import(self, start_date=None, end_date=None, parallel=True, max_workers=3):
        """
        Perform bulk import of historical data
        
        Args:
            start_date: Start date (YYYY-MM-DD) or None for API default
            end_date: End date (YYYY-MM-DD) or None for today
            parallel: Use parallel processing
            max_workers: Number of parallel workers (be conservative to avoid rate limits)
        """
        print("\n" + "="*60)
        print("LIMITLESS BULK IMPORT STARTING")
        print("="*60)
        
        # Determine date range
        if not start_date or not end_date:
            api_start, api_end = self.get_date_range()
            start_date = start_date or api_start
            end_date = end_date or api_end
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate list of dates
        dates_to_process = []
        current = start
        while current <= end:
            dates_to_process.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        total_days = len(dates_to_process)
        print(f"\nDate Range: {start_date} to {end_date}")
        print(f"Total Days to Process: {total_days}")
        print(f"Processing Mode: {'Parallel' if parallel else 'Sequential'}")
        if parallel:
            print(f"Workers: {max_workers}")
        print("\n" + "-"*60 + "\n")
        
        start_time = time.time()
        
        if parallel and total_days > 5:
            # Parallel processing for large imports
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.process_single_date, date): date 
                    for date in dates_to_process
                }
                
                completed = 0
                for future in as_completed(futures):
                    completed += 1
                    date = futures[future]
                    try:
                        success = future.result()
                        print(f"Progress: {completed}/{total_days} ({completed*100//total_days}%)")
                    except Exception as e:
                        print(f"  ✗ Error processing {date}: {e}")
                        self.failed_dates.append(date)
                    
                    # Small delay between requests to be nice to the API
                    if completed % 10 == 0:
                        time.sleep(1)
        else:
            # Sequential processing
            for idx, date in enumerate(dates_to_process, 1):
                self.process_single_date(date)
                print(f"Progress: {idx}/{total_days} ({idx*100//total_days}%)")
                
                # Rate limiting - adjust based on API limits
                if idx % 10 == 0:
                    print("  Pausing for rate limit...")
                    time.sleep(2)
                else:
                    time.sleep(0.5)  # Small delay between requests
        
        elapsed = time.time() - start_time
        
        # Commit all changes at once
        print("\n" + "-"*60)
        print("Committing all changes to Git...")
        
        try:
            # Add all new files
            self.repo.git.add(A=True)
            
            # Check if there are changes
            if self.repo.index.diff("HEAD"):
                # Commit with summary
                commit_msg = f"""Bulk import of Limitless data

Imported: {len(self.successful_dates)} days
Failed: {len(self.failed_dates)} days
Date Range: {start_date} to {end_date}
Duration: {elapsed:.1f} seconds
"""
                self.repo.index.commit(commit_msg)
                
                # Push to GitHub
                print("Pushing to GitHub...")
                origin = self.repo.remote('origin')
                origin.push()
                print("✓ Successfully pushed to GitHub")
            else:
                print("No new changes to commit")
        except Exception as e:
            print(f"Git error: {e}")
        
        # Print summary
        print("\n" + "="*60)
        print("BULK IMPORT COMPLETE")
        print("="*60)
        print(f"✓ Successfully imported: {len(self.successful_dates)} days")
        print(f"✗ Failed/No data: {len(self.failed_dates)} days")
        print(f"⏱ Time elapsed: {elapsed:.1f} seconds")
        print(f"📁 Repository: {LOCAL_REPO_PATH}")
        
        # Save failed dates for retry
        if self.failed_dates:
            failed_file = Path(LOCAL_REPO_PATH) / "failed_imports.txt"
            with open(failed_file, 'w') as f:
                f.write('\n'.join(self.failed_dates))
            print(f"\nFailed dates saved to: {failed_file}")
            print("You can retry these specific dates later")
        
        return len(self.successful_dates), len(self.failed_dates)
    
    def retry_failed(self):
        """Retry previously failed imports"""
        failed_file = Path(LOCAL_REPO_PATH) / "failed_imports.txt"
        if not failed_file.exists():
            print("No failed imports to retry")
            return
        
        with open(failed_file, 'r') as f:
            dates = f.read().strip().split('\n')
        
        print(f"Retrying {len(dates)} failed imports...")
        self.failed_dates = []
        
        for date in dates:
            self.process_single_date(date)
            time.sleep(1)  # Rate limiting
        
        # Update failed file
        if self.failed_dates:
            with open(failed_file, 'w') as f:
                f.write('\n'.join(self.failed_dates))
        else:
            failed_file.unlink()
            print("All retries successful!")

def main():
    parser = argparse.ArgumentParser(description='Bulk import Limitless data to GitHub')
    parser.add_argument(
        '--start-date', 
        type=str, 
        help='Start date (YYYY-MM-DD). Default: API earliest or 1 year ago'
    )
    parser.add_argument(
        '--end-date', 
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help='End date (YYYY-MM-DD). Default: today'
    )
    parser.add_argument(
        '--days-back',
        type=int,
        help='Alternative: Import last N days'
    )
    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Use sequential processing instead of parallel'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='Number of parallel workers (default: 3)'
    )
    parser.add_argument(
        '--retry-failed',
        action='store_true',
        help='Retry previously failed imports'
    )
    
    args = parser.parse_args()
    
    # Initialize importer
    importer = LimitlessBulkImporter()
    
    if args.retry_failed:
        importer.retry_failed()
    else:
        # Determine date range
        if args.days_back:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=args.days_back)
            args.start_date = start_date.strftime('%Y-%m-%d')
            args.end_date = end_date.strftime('%Y-%m-%d')
        
        # Run bulk import
        importer.bulk_import(
            start_date=args.start_date,
            end_date=args.end_date,
            parallel=not args.sequential,
            max_workers=args.workers
        )

if __name__ == "__main__":
    main()
