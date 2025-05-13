"""
Service for handling match predictions.
"""
import json
import os
from datetime import datetime

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# File paths
PREDICTIONS_FILE = os.path.join(DATA_DIR, 'predictions.json')
MATCHES_FILE = os.path.join(DATA_DIR, 'matches.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def load_data(file_path, default=None):
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

def save_data(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_matches():
    """Get all matches."""
    return load_data(MATCHES_FILE)

def get_upcoming_matches():
    """Get matches that haven't started yet."""
    matches = get_matches()
    now = datetime.now()
    
    upcoming = {}
    for match_id, match in matches.items():
        match_time = datetime.strptime(match['time'], '%Y-%m-%d %H:%M')
        if match_time > now and not match.get('locked', False):
            upcoming[match_id] = match
    
    return upcoming

def add_match(team1, team2, time, is_knockout=False):
    """Add a new match."""
    matches = get_matches()
    
    # Generate a unique match ID
    match_id = str(len(matches) + 1)
    while match_id in matches:
        match_id = str(int(match_id) + 1)
    
    matches[match_id] = {
        'team1': team1,
        'team2': team2,
        'time': time,
        'is_knockout': is_knockout,
        'locked': False
    }
    
    save_data(MATCHES_FILE, matches)
    return match_id

def set_match_result(match_id, home_goals, away_goals, resolution_type=None):
    """Set the result for a match."""
    matches = get_matches()
    
    if match_id not in matches:
        return False
    
    matches[match_id]['result'] = {
        'home_goals': home_goals,
        'away_goals': away_goals
    }
    
    if matches[match_id].get('is_knockout', False) and resolution_type:
        matches[match_id]['result']['resolution_type'] = resolution_type
    
    matches[match_id]['locked'] = True
    save_data(MATCHES_FILE, matches)
    
    # Update leaderboard after setting match result
    from .scoring import update_leaderboard
    update_leaderboard()
    
    return True

def save_prediction(user_id, match_id, home_goals, away_goals, resolution_type=None):
    """Save a user's prediction for a match."""
    predictions = load_data(PREDICTIONS_FILE)
    
    if user_id not in predictions:
        predictions[user_id] = {}
    
    predictions[user_id][match_id] = {
        'home_goals': home_goals,
        'away_goals': away_goals
    }
    
    matches = get_matches()
    if matches.get(match_id, {}).get('is_knockout', False) and resolution_type:
        predictions[user_id][match_id]['resolution_type'] = resolution_type
    
    save_data(PREDICTIONS_FILE, predictions)
    return True

def get_user_predictions(user_id):
    """Get all predictions for a user."""
    predictions = load_data(PREDICTIONS_FILE)
    return predictions.get(user_id, {})

def register_user(user_id, username, first_name, last_name=None):
    """Register a new user or update existing user info."""
    users = load_data(USERS_FILE)
    
    users[str(user_id)] = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'registered_at': datetime.now().isoformat(),
        'is_admin': False  # Default value
    }
    
    save_data(USERS_FILE, users)
    return True

def is_admin(user_id):
    """Check if a user is an admin by ID."""
    users = load_data(USERS_FILE)
    return users.get(str(user_id), {}).get('is_admin', False)

def is_admin_by_username(username):
    """Check if a user is an admin by username."""
    if not username:
        return False
        
    users = load_data(USERS_FILE)
    
    # Look for a user with matching username
    for user_data in users.values():
        if user_data.get('username') == username and user_data.get('is_admin', False):
            return True
    
    return False

def set_admin(user_id, is_admin_value=True):
    """Set a user as admin by ID."""
    users = load_data(USERS_FILE)
    
    if str(user_id) in users:
        users[str(user_id)]['is_admin'] = is_admin_value
        save_data(USERS_FILE, users)
        return True
    
    return False

def set_admin_by_username(username, is_admin_value=True):
    """Set a user as admin by username."""
    if not username:
        return False
        
    users = load_data(USERS_FILE)
    found = False
    
    # Look for a user with matching username
    for user_id, user_data in users.items():
        if user_data.get('username') == username:
            user_data['is_admin'] = is_admin_value
            found = True
    
    if found:
        save_data(USERS_FILE, users)
        return True
    
    # If user not found, create a placeholder user record that will be updated
    # when the user interacts with the bot
    user_id = f"placeholder_{username}"
    users[user_id] = {
        'username': username,
        'first_name': username,
        'registered_at': datetime.now().isoformat(),
        'is_admin': is_admin_value
    }
    save_data(USERS_FILE, users)
    return True

def lock_expired_matches():
    """Lock matches that have already started."""
    matches = get_matches()
    now = datetime.now()
    updated = False
    
    for match_id, match in matches.items():
        match_time = datetime.strptime(match['time'], '%Y-%m-%d %H:%M')
        if match_time <= now and not match.get('locked', False):
            match['locked'] = True
            updated = True
    
    if updated:
        save_data(MATCHES_FILE, matches)
    
    return updated 