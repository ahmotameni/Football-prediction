"""
Service for calculating scores and updating the leaderboard using Firebase Realtime Database.
"""
from datetime import datetime
from club_world_cup_bot.config.scoring_rules import SCORING_RULES

# Import Firebase helpers
from firebase_helpers import (
    get_all_users, save_user,
    get_all_matches,
    get_all_predictions
)

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
    
    # Check if prediction is completely wrong for 90 minutes result
    if pred_winner != result_winner:
        return SCORING_RULES["WRONG_PREDICTION"]
    
    # Correct winner for 90 minutes
    score += SCORING_RULES["CORRECT_WINNER"]
    
    # Correct goal difference
    pred_diff = pred_home - pred_away
    result_diff = result_home - result_away
    if pred_diff == result_diff:
        score += SCORING_RULES["CORRECT_GOAL_DIFF"]
    
    # Exact score
    if pred_home == result_home and pred_away == result_away:
        score += SCORING_RULES["EXACT_SCORE"]
    
    # For knockout matches, check resolution type regardless of tie/non-tie
    if 'resolution_type' in result and 'resolution_type' in prediction:
        # For ties in 90 minutes
        if result_winner == 0 and pred_winner == 0:
            # Check both resolution type and knockout winner
            if (prediction['resolution_type'] == result['resolution_type'] and
                prediction.get('knockout_winner') == result.get('knockout_winner')):
                score += SCORING_RULES["CORRECT_RESOLUTION_TYPE"]
        # For non-tie matches, just check if resolution type is correct (should be FT)
        elif prediction['resolution_type'] == result['resolution_type']:
            score += SCORING_RULES["CORRECT_RESOLUTION_TYPE"]
    
    return score

def update_leaderboard():
    """Update scores for all users based on match results."""
    predictions = get_all_predictions()
    matches = get_all_matches()
    users = get_all_users()
    
    # Calculate scores for each user and match
    for user_id, user_predictions in predictions.items():
        if user_id not in users:
            continue
            
        total_score = 0
        for match_id, prediction in user_predictions.items():
            if match_id in matches and 'result' in matches[match_id]:
                match_score = calculate_score(prediction, matches[match_id]['result'])
                total_score += match_score
        
        # Update user score in Firebase
        user_data = users[user_id].copy()
        user_data['score'] = total_score
        save_user(user_id, user_data)
    
    return True

def get_leaderboard():
    """Get sorted leaderboard with user scores."""
    users = get_all_users()
    
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