"""
Firebase helper functions for the Club World Cup Bot.

This module provides high-level functions for interacting with Firebase Realtime Database,
abstracting the database operations from the application logic.
"""
from firebase_admin import db
from firebase_init import get_database

def get_all_users():
    """Get all users from Firebase."""
    try:
        database = get_database()
        users_ref = database.child('users')
        users = users_ref.get() or {}
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        return {}

def save_user(user_id, data):
    """Save or update a user in Firebase."""
    try:
        database = get_database()
        users_ref = database.child('users')
        users_ref.child(str(user_id)).update(data)
        return True
    except Exception as e:
        print(f"Error saving user {user_id}: {e}")
        return False

def get_user(user_id):
    """Get a specific user from Firebase."""
    try:
        database = get_database()
        users_ref = database.child('users')
        user = users_ref.child(str(user_id)).get() or {}
        return user
    except Exception as e:
        print(f"Error getting user {user_id}: {e}")
        return {}

def get_all_matches():
    """Get all matches from Firebase."""
    try:
        database = get_database()
        matches_ref = database.child('matches')
        matches = matches_ref.get() or {}
        return matches
    except Exception as e:
        print(f"Error getting matches: {e}")
        return {}

def save_match(match_id, data):
    """Save or update a match in Firebase."""
    try:
        database = get_database()
        matches_ref = database.child('matches')
        matches_ref.child(str(match_id)).set(data)
        return True
    except Exception as e:
        print(f"Error saving match {match_id}: {e}")
        return False

def add_match(data):
    """Add a new match to Firebase and return the generated ID."""
    try:
        database = get_database()
        matches_ref = database.child('matches')
        
        # Get existing matches to generate next ID
        existing_matches = matches_ref.get() or {}
        next_id = str(len(existing_matches) + 1)
        
        # Find a unique ID
        while next_id in existing_matches:
            next_id = str(int(next_id) + 1)
        
        matches_ref.child(next_id).set(data)
        return next_id
    except Exception as e:
        print(f"Error adding match: {e}")
        return None

def update_match(match_id, data):
    """Update specific fields of a match in Firebase."""
    try:
        database = get_database()
        matches_ref = database.child('matches')
        matches_ref.child(str(match_id)).update(data)
        return True
    except Exception as e:
        print(f"Error updating match {match_id}: {e}")
        return False

def get_all_predictions():
    """Get all predictions from Firebase."""
    try:
        database = get_database()
        predictions_ref = database.child('predictions')
        predictions = predictions_ref.get() or {}
        return predictions
    except Exception as e:
        print(f"Error getting predictions: {e}")
        return {}

def get_predictions(user_id):
    """Get all predictions for a specific user from Firebase."""
    try:
        database = get_database()
        predictions_ref = database.child('predictions')
        user_predictions = predictions_ref.child(str(user_id)).get() or {}
        return user_predictions
    except Exception as e:
        print(f"Error getting predictions for user {user_id}: {e}")
        return {}

def save_prediction(user_id, match_id, data):
    """Save a prediction for a user and match in Firebase."""
    try:
        database = get_database()
        predictions_ref = database.child('predictions')
        predictions_ref.child(str(user_id)).child(str(match_id)).set(data)
        return True
    except Exception as e:
        print(f"Error saving prediction for user {user_id}, match {match_id}: {e}")
        return False

def get_current_stage():
    """Get the current tournament stage from Firebase."""
    try:
        database = get_database()
        stage_ref = database.child('current_stage')
        stage_data = stage_ref.get() or {"current_stage": 1}
        return stage_data.get("current_stage", 1)
    except Exception as e:
        print(f"Error getting current stage: {e}")
        return 1

def set_current_stage(stage):
    """Set the current tournament stage in Firebase."""
    try:
        database = get_database()
        stage_ref = database.child('current_stage')
        stage_ref.set({"current_stage": stage})
        return True
    except Exception as e:
        print(f"Error setting current stage: {e}")
        return False

def clear_all_data():
    """Clear all data from Firebase (for testing purposes)."""
    try:
        database = get_database()
        database.set({})
        return True
    except Exception as e:
        print(f"Error clearing data: {e}")
        return False 