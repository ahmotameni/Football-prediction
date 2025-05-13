"""
Debug script to identify what's changing the dates in matches.json.
"""
import os
import json
import sys
import shutil
from datetime import datetime

# Ensure we're in the correct directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Define paths
DATA_DIR = os.path.join(SCRIPT_DIR, 'club_world_cup_bot/data')
MATCHES_FILE = os.path.join(DATA_DIR, 'matches.json')
DEBUG_LOG = os.path.join(SCRIPT_DIR, 'debug_log.txt')

def log(message):
    """Log a message to the debug log and print it."""
    with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def save_json(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(file_path, default=None):
    """Load data from a JSON file."""
    if default is None:
        default = {}
    
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return default

def check_dates(matches, label):
    """Check the dates in the matches object and report years."""
    years = {}
    for match_id, match in matches.items():
        if "time" in match:
            year = match["time"][:4]
            years[year] = years.get(year, 0) + 1
    
    log(f"[{label}] Years in matches: {years}")
    return years

def make_backup():
    """Make a backup of the current matches.json file."""
    if os.path.exists(MATCHES_FILE):
        backup_file = f"{MATCHES_FILE}.backup"
        shutil.copy(MATCHES_FILE, backup_file)
        log(f"Made backup of matches.json to {backup_file}")
        return backup_file
    return None

def restore_backup(backup_file):
    """Restore matches.json from backup."""
    if backup_file and os.path.exists(backup_file):
        shutil.copy(backup_file, MATCHES_FILE)
        log(f"Restored matches.json from backup")

def update_years_to_2025():
    """Update all match dates to 2025."""
    matches = load_json(MATCHES_FILE)
    check_dates(matches, "Before update")
    
    for match_id in matches:
        if "time" in matches[match_id]:
            time_str = matches[match_id]["time"]
            if time_str.startswith("2024"):
                matches[match_id]["time"] = "2025" + time_str[4:]
    
    save_json(MATCHES_FILE, matches)
    check_dates(matches, "After update")
    log("Updated all match dates to 2025")

def check_matches_file():
    """Check the matches file before and after running the command."""
    log("\n=== CHECKING MATCHES FILE BEFORE RUNNING COMMAND ===")
    
    if not os.path.exists(MATCHES_FILE):
        log(f"Matches file does not exist: {MATCHES_FILE}")
        return
    
    # Check current content
    matches = load_json(MATCHES_FILE)
    check_dates(matches, "Initial state")
    
    # Make a backup
    backup_file = make_backup()
    
    # Update to 2025
    update_years_to_2025()
    
    log("\n=== RUNNING STAGED TEST SCRIPT ===")
    log(f"Command: {' '.join(sys.argv[1:])}")
    
    # Run the actual staged_test.py script with the same arguments
    os.system(f"python run_staged_test.py {' '.join(sys.argv[1:])}")
    
    log("\n=== CHECKING MATCHES FILE AFTER RUNNING COMMAND ===")
    
    # Check updated content
    matches_after = load_json(MATCHES_FILE)
    check_dates(matches_after, "After staged_test")
    
    log("\n=== RESTORING BACKUP AND UPDATING TO 2025 ===")
    restore_backup(backup_file)
    update_years_to_2025()
    
    log("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    # Clear previous log
    with open(DEBUG_LOG, 'w', encoding='utf-8') as f:
        f.write("=== DEBUG LOG ===\n")
    
    check_matches_file() 