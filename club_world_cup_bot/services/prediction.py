"""
Service for handling match predictions using Firebase Realtime Database.
"""
from datetime import datetime
from ..firebase_helpers import (
    get_all_users, save_user, get_user,
    get_all_matches, save_match, add_match, update_match,
    get_all_predictions, get_predictions, save_prediction
)

def get_matches():
    """Get all matches."""
    return get_all_matches()

def get_upcoming_matches():
    """Get matches that haven't started yet."""
    matches = get_matches()
    
    # Handle case where get_matches returns None or empty
    if not matches or not isinstance(matches, dict):
        return {}
    
    now = datetime.now()
    upcoming = {}
    
    for match_id, match in matches.items():
        try:
            match_time = datetime.strptime(match['time'], '%Y-%m-%d %H:%M')
            if match_time > now and not match.get('locked', False):
                upcoming[match_id] = match
        except (ValueError, KeyError) as e:
            print(f"Error processing match {match_id}: {e}")
            continue
    
    return upcoming

def add_match(team1, team2, time, is_knockout=False):
    """Add a new match."""
    from ..firebase_helpers import add_match as firebase_add_match
    
    match_data = {
        'team1': team1,
        'team2': team2,
        'time': time,
        'is_knockout': is_knockout,
        'locked': False
    }
    
    return firebase_add_match(match_data)

def set_match_result(match_id, home_goals, away_goals, resolution_type=None):
    """Set the result for a match."""
    matches = get_matches()
    
    if match_id not in matches:
        return False
    
    match_data = matches[match_id].copy()
    match_data['result'] = {
        'home_goals': home_goals,
        'away_goals': away_goals
    }
    
    if match_data.get('is_knockout', False) and resolution_type:
        # Parse resolution_type for knockout winner if available
        if "_" in resolution_type:
            parts = resolution_type.split("_", 1)  # Split only on first underscore
            res_type = parts[0]
            knockout_winner = parts[1]
            match_data['result']['resolution_type'] = res_type
            match_data['result']['knockout_winner'] = knockout_winner
        else:
            match_data['result']['resolution_type'] = resolution_type
    
    match_data['locked'] = True
    
    # Save the updated match to Firebase
    if not save_match(match_id, match_data):
        return False
    
    # Update leaderboard after setting match result
    from .scoring import update_leaderboard
    update_leaderboard()
    
    return True

def save_prediction(user_id, match_id, home_goals, away_goals, resolution_type=None):
    """Save a user's prediction for a match."""
    from ..firebase_helpers import save_prediction as firebase_save_prediction
    
    prediction_data = {
        'home_goals': home_goals,
        'away_goals': away_goals
    }
    
    matches = get_matches()
    if matches.get(match_id, {}).get('is_knockout', False) and resolution_type:
        # Parse resolution_type for knockout winner if available
        if "_" in resolution_type:
            parts = resolution_type.split("_", 1)  # Split only on first underscore
            res_type = parts[0]
            knockout_winner = parts[1]
            prediction_data['resolution_type'] = res_type
            prediction_data['knockout_winner'] = knockout_winner
        else:
            prediction_data['resolution_type'] = resolution_type
    
    return firebase_save_prediction(user_id, match_id, prediction_data)

def get_user_predictions(user_id):
    """Get all predictions for a user."""
    return get_predictions(user_id)

def register_user(user_id, username, first_name, last_name=None):
    """Register a new user or update existing user info."""
    user_data = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'registered_at': datetime.now().isoformat(),
        'is_admin': False,  # Default value
        'score': 0  # Default score
    }
    
    return save_user(user_id, user_data)

def is_admin(user_id):
    """Check if a user is an admin by ID."""
    user = get_user(user_id)
    return user.get('is_admin', False)

def is_admin_by_username(username):
    """Check if a user is an admin by username."""
    if not username:
        return False
        
    users = get_all_users()
    
    # Look for a user with matching username
    for user_data in users.values():
        if user_data.get('username') == username and user_data.get('is_admin', False):
            return True
    
    return False

def set_admin(user_id, is_admin_value=True):
    """Set a user as admin by ID."""
    user = get_user(user_id)
    
    if user:
        user['is_admin'] = is_admin_value
        return save_user(user_id, user)
    
    return False

def set_admin_by_username(username, is_admin_value=True):
    """Set a user as admin by username."""
    if not username:
        return False
        
    users = get_all_users()
    found = False
    
    # Look for a user with matching username
    for user_id, user_data in users.items():
        if user_data.get('username') == username:
            user_data['is_admin'] = is_admin_value
            save_user(user_id, user_data)
            found = True
    
    if found:
        return True
    
    # If user not found, create a placeholder user record that will be updated
    # when the user interacts with the bot
    user_id = f"placeholder_{username}"
    user_data = {
        'username': username,
        'first_name': username,
        'registered_at': datetime.now().isoformat(),
        'is_admin': is_admin_value,
        'score': 0
    }
    return save_user(user_id, user_data)

def lock_expired_matches():
    """Lock matches that have already started."""
    matches = get_matches()
    
    # Handle case where get_matches returns None or empty
    if not matches or not isinstance(matches, dict):
        return False
    
    now = datetime.now()
    updated = False
    
    for match_id, match in matches.items():
        try:
            match_time = datetime.strptime(match['time'], '%Y-%m-%d %H:%M')
            if match_time <= now and not match.get('locked', False):
                match['locked'] = True
                save_match(match_id, match)
                updated = True
        except (ValueError, KeyError) as e:
            print(f"Error processing match {match_id}: {e}")
            continue
    
    return updated 