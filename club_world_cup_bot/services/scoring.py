"""
Service for calculating scores and updating the leaderboard.
"""
import json
import os
from datetime import datetime
from club_world_cup_bot.config.scoring_rules import SCORING_RULES

# Import from prediction service
from club_world_cup_bot.services.prediction import load_data, save_data, PREDICTIONS_FILE, MATCHES_FILE, USERS_FILE

def calculate_score(prediction, result):
    """Calculate score for a single prediction."""
    score = 0
    
    # Extract prediction values
    pred_home = prediction['home_goals']
    pred_away = prediction['away_goals']
    
    # Extract result values
    result_home = result['home_goals']
    result_away = result['away_goals']
    
    # Determine the winner (1 for home, 2 for away, 0 for draw)
    pred_winner = 1 if pred_home > pred_away else (2 if pred_home < pred_away else 0)
    result_winner = 1 if result_home > result_away else (2 if result_home < result_away else 0)
    
    # Check if prediction is completely wrong
    if pred_winner != result_winner:
        return SCORING_RULES["WRONG_PREDICTION"]
    
    # Correct winner
    score += SCORING_RULES["CORRECT_WINNER"]
    
    # Correct goal difference
    pred_diff = pred_home - pred_away
    result_diff = result_home - result_away
    if pred_diff == result_diff:
        score += SCORING_RULES["CORRECT_GOAL_DIFF"]
    
    # Exact score
    if pred_home == result_home and pred_away == result_away:
        score += SCORING_RULES["EXACT_SCORE"]
    
    # For knockout matches, check resolution type
    if 'resolution_type' in result and 'resolution_type' in prediction:
        if prediction['resolution_type'] == result['resolution_type']:
            score += SCORING_RULES["CORRECT_RESOLUTION_TYPE"]
    
    return score

def update_leaderboard():
    """Update scores for all users based on match results."""
    predictions = load_data(PREDICTIONS_FILE)
    matches = load_data(MATCHES_FILE)
    users = load_data(USERS_FILE)
    
    # Reset scores
    for user_id in users:
        users[user_id]['score'] = 0
    
    # Calculate scores for each user and match
    for user_id, user_predictions in predictions.items():
        if user_id not in users:
            continue
            
        total_score = 0
        for match_id, prediction in user_predictions.items():
            if match_id in matches and 'result' in matches[match_id]:
                match_score = calculate_score(prediction, matches[match_id]['result'])
                total_score += match_score
        
        users[user_id]['score'] = total_score
    
    # Save updated user scores
    save_data(USERS_FILE, users)
    return True

def get_leaderboard():
    """Get sorted leaderboard with user scores."""
    users = load_data(USERS_FILE)
    
    # Filter out users without scores and sort by score
    leaderboard = [
        {
            'user_id': user_id,
            'name': user.get('first_name', 'Unknown'),
            'username': user.get('username', ''),
            'score': user.get('score', 0)
        }
        for user_id, user in users.items()
        if 'score' in user
    ]
    
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    
    # Add rank
    for i, entry in enumerate(leaderboard):
        entry['rank'] = i + 1
    
    return leaderboard

def get_user_rank(user_id):
    """Get a user's rank in the leaderboard."""
    leaderboard = get_leaderboard()
    
    for entry in leaderboard:
        if entry['user_id'] == str(user_id):
            return entry['rank'], entry['score']
    
    return None, 0 