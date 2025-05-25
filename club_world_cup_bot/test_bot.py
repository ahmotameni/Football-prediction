"""
Test script for the Club World Cup 2025 Prediction Bot.

This script creates test data and simulates various usage scenarios.
Run it to populate your Firebase database with fake data for testing.

Usage:
    python test_bot.py
"""
import random
import datetime
from datetime import timedelta

# Import Firebase helpers for data operations
from .firebase_helpers import (
    get_all_users, save_user,
    get_all_matches, save_match,
    get_all_predictions, save_prediction,
    clear_all_data
)

def create_test_users():
    """Create test users."""
    print("Creating test users...")
    users = {
        "123456789": {
            "username": "admin_user",
            "first_name": "Admin",
            "last_name": "User",
            "registered_at": datetime.datetime.now().isoformat(),
            "is_admin": True,
            "whitelisted": True,
            "score": 0
        },
        "987654321": {
            "username": "regular_user",
            "first_name": "Regular",
            "last_name": "User",
            "registered_at": datetime.datetime.now().isoformat(),
            "is_admin": False,
            "whitelisted": True,
            "score": 0
        },
        "111222333": {
            "username": "Ahmotameni",  # Match the admin username in credentials.env
            "first_name": "Amir",
            "last_name": "Motameni",
            "registered_at": datetime.datetime.now().isoformat(),
            "is_admin": True,
            "whitelisted": True,
            "score": 0
        }
    }
    
    # Add 5 more random users
    for i in range(5):
        user_id = str(random.randint(100000000, 999999999))
        users[user_id] = {
            "username": f"user_{i}",
            "first_name": f"User {i}",
            "registered_at": datetime.datetime.now().isoformat(),
            "is_admin": False,
            "whitelisted": True,
            "score": 0
        }
    
    # Save each user to Firebase
    for user_id, user_data in users.items():
        save_user(user_id, user_data)
    
    print(f"Created {len(users)} test users.")
    return users

def create_test_matches():
    """Create test matches for the Club World Cup."""
    print("Creating test matches...")
    
    # Club World Cup Teams (16 teams)
    teams = [
        "Manchester City",
        "Real Madrid",
        "Bayern Munich",
        "Flamengo",
        "Al-Ahly",
        "Auckland City",
        "Urawa Red Diamonds",
        "Al-Hilal",
        "Seattle Sounders",
        "Wydad Casablanca",
        "Mamelodi Sundowns",
        "Ulsan Hyundai",
        "Monterrey",
        "Palmeiras",
        "Esperance",
        "Inter Milan"
    ]
    
    # Add group stage matches (every team plays 3 matches)
    now = datetime.datetime.now()
    match_id = 1
    
    # Group stage (past matches, with results)
    for i in range(0, 16, 4):  # 4 groups
        for j in range(4):
            for k in range(j+1, 4):
                match_time = now - timedelta(days=random.randint(1, 10))
                
                # Create match data
                match_data = {
                    "team1": teams[i+j],
                    "team2": teams[i+k],
                    "time": match_time.strftime("%Y-%m-%d %H:%M"),
                    "is_knockout": False,
                    "locked": True
                }
                
                # Add result
                home_goals = random.randint(0, 4)
                away_goals = random.randint(0, 4)
                match_data["result"] = {
                    "home_goals": home_goals,
                    "away_goals": away_goals
                }
                
                # Save to Firebase
                save_match(str(match_id), match_data)
                match_id += 1
    
    # Knockout stage (upcoming matches, no results yet)
    knockout_teams = teams[:8]  # Top 8 teams qualify
    
    # Quarter-finals (in the future)
    for i in range(0, 8, 2):
        match_time = now + timedelta(days=random.randint(1, 5))
        
        match_data = {
            "team1": knockout_teams[i],
            "team2": knockout_teams[i+1],
            "time": match_time.strftime("%Y-%m-%d %H:%M"),
            "is_knockout": True,
            "locked": False
        }
        
        save_match(str(match_id), match_data)
        match_id += 1
    
    # Semi-finals (further in the future)
    semi_final_teams = knockout_teams[:4]  # First 4 teams qualify
    for i in range(0, 4, 2):
        match_time = now + timedelta(days=random.randint(7, 10))
        
        match_data = {
            "team1": semi_final_teams[i],
            "team2": semi_final_teams[i+1],
            "time": match_time.strftime("%Y-%m-%d %H:%M"),
            "is_knockout": True,
            "locked": False
        }
        
        save_match(str(match_id), match_data)
        match_id += 1
    
    # Final (even further in the future)
    final_teams = semi_final_teams[:2]  # First 2 teams qualify
    match_time = now + timedelta(days=random.randint(14, 20))
    
    match_data = {
        "team1": final_teams[0],
        "team2": final_teams[1],
        "time": match_time.strftime("%Y-%m-%d %H:%M"),
        "is_knockout": True,
        "locked": False
    }
    
    save_match(str(match_id), match_data)
    
    matches = get_all_matches()
    print(f"Created {len(matches)} test matches.")
    return matches

def create_test_predictions(users, matches):
    """Create test predictions for users."""
    print("Creating test predictions...")
    
    prediction_count = 0
    
    # For each user
    for user_id, user in users.items():
        # For each match
        for match_id, match in matches.items():
            # Skip some matches randomly
            if random.random() < 0.3:
                continue
                
            # Only predict for locked matches (past matches)
            if match.get("locked", False):
                home_goals = random.randint(0, 4)
                away_goals = random.randint(0, 4)
                
                prediction_data = {
                    "home_goals": home_goals,
                    "away_goals": away_goals
                }
                
                # Add resolution type for knockout matches
                if match.get("is_knockout", False):
                    resolution_types = ["FT", "ET", "PEN"]
                    prediction_data["resolution_type"] = random.choice(resolution_types)
                
                # Save to Firebase
                save_prediction(user_id, match_id, prediction_data)
                prediction_count += 1
    
    print(f"Created {prediction_count} test predictions.")
    return get_all_predictions()

def calculate_scores(predictions, matches):
    """Calculate scores based on predictions and match results."""
    print("Calculating scores...")
    
    # Scoring rules
    SCORING_RULES = {
        "CORRECT_WINNER": 2,
        "CORRECT_GOAL_DIFF": 1,
        "EXACT_SCORE": 2,
        "CORRECT_RESOLUTION_TYPE": 1,
        "WRONG_PREDICTION": -1
    }
    
    # Calculate scores for each user
    users = get_all_users()
    
    for user_id, user_predictions in predictions.items():
        total_score = 0
        
        for match_id, prediction in user_predictions.items():
            match = matches.get(match_id)
            
            # Skip if no result yet
            if not match or "result" not in match:
                continue
            
            result = match["result"]
            
            # Extract values
            pred_home = prediction["home_goals"]
            pred_away = prediction["away_goals"]
            result_home = result["home_goals"]
            result_away = result["away_goals"]
            
            # Determine winners
            pred_winner = 1 if pred_home > pred_away else (2 if pred_home < pred_away else 0)
            result_winner = 1 if result_home > result_away else (2 if result_home < result_away else 0)
            
            # Calculate score
            if pred_winner != result_winner:
                total_score += SCORING_RULES["WRONG_PREDICTION"]
                continue
            
            # Correct winner
            total_score += SCORING_RULES["CORRECT_WINNER"]
            
            # Correct goal difference
            pred_diff = pred_home - pred_away
            result_diff = result_home - result_away
            if pred_diff == result_diff:
                total_score += SCORING_RULES["CORRECT_GOAL_DIFF"]
            
            # Exact score
            if pred_home == result_home and pred_away == result_away:
                total_score += SCORING_RULES["EXACT_SCORE"]
            
            # Resolution type (knockout only)
            if match.get("is_knockout", False) and "resolution_type" in result and "resolution_type" in prediction:
                if prediction["resolution_type"] == result["resolution_type"]:
                    total_score += SCORING_RULES["CORRECT_RESOLUTION_TYPE"]
        
        # Save user score
        if user_id in users:
            users[user_id]["score"] = total_score
            # Update user score in Firebase
            save_user(user_id, users[user_id])
    
    print("Scores calculated and saved.")

def display_leaderboard():
    """Display the current leaderboard."""
    print("\n=== LEADERBOARD ===")
    
    users = get_all_users()
    
    # Create leaderboard
    leaderboard = []
    for user_id, user in users.items():
        leaderboard.append({
            "user_id": user_id,
            "name": user.get("first_name", "Unknown"),
            "username": user.get("username", ""),
            "score": user.get("score", 0)
        })
    
    # Sort by score
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    
    # Display
    for i, entry in enumerate(leaderboard):
        print(f"{i+1}. {entry['name']} (@{entry['username']}): {entry['score']} pts")

def simulate_match_prediction():
    """Simulate a user making a prediction."""
    print("\n=== SIMULATING MATCH PREDICTION ===")
    
    # Load data
    users = get_all_users()
    matches = get_all_matches()
    
    # Find an unlocked match
    unlocked_matches = {}
    for match_id, match in matches.items():
        if not match.get("locked", False):
            unlocked_matches[match_id] = match
    
    if not unlocked_matches:
        print("No unlocked matches available.")
        return
    
    # Select a random match
    match_id = random.choice(list(unlocked_matches.keys()))
    match = unlocked_matches[match_id]
    
    # Select a random user
    user_id = random.choice(list(users.keys()))
    user = users[user_id]
    
    # Make a prediction
    home_goals = random.randint(0, 4)
    away_goals = random.randint(0, 4)
    
    prediction_data = {
        "home_goals": home_goals,
        "away_goals": away_goals
    }
    
    if match.get("is_knockout", False):
        resolution_types = ["FT", "ET", "PEN"]
        prediction_data["resolution_type"] = random.choice(resolution_types)
    
    # Save prediction to Firebase
    save_prediction(user_id, match_id, prediction_data)
    
    # Display the prediction
    print(f"User {user['first_name']} (@{user['username']}) predicted:")
    print(f"{match['team1']} {home_goals} - {away_goals} {match['team2']}")
    
    if match.get("is_knockout", False) and "resolution_type" in prediction_data:
        resolution_text = {
            "FT": "Full Time",
            "ET": "Extra Time",
            "PEN": "Penalties"
        }[prediction_data["resolution_type"]]
        print(f"Resolution: {resolution_text}")

def simulate_setting_result():
    """Simulate setting a result for a match."""
    print("\n=== SIMULATING SETTING MATCH RESULT ===")
    
    # Load data
    matches = get_all_matches()
    
    # Find an unlocked match
    unlocked_matches = {}
    for match_id, match in matches.items():
        if not match.get("locked", False):
            unlocked_matches[match_id] = match
    
    if not unlocked_matches:
        print("No unlocked matches available.")
        return
    
    # Select a random match
    match_id = random.choice(list(unlocked_matches.keys()))
    match = unlocked_matches[match_id]
    
    # Set result
    home_goals = random.randint(0, 4)
    away_goals = random.randint(0, 4)
    
    match["result"] = {
        "home_goals": home_goals,
        "away_goals": away_goals
    }
    
    if match.get("is_knockout", False):
        resolution_types = ["FT", "ET", "PEN"]
        match["result"]["resolution_type"] = random.choice(resolution_types)
    
    match["locked"] = True
    
    # Save updated match to Firebase
    save_match(match_id, match)
    
    # Display the result
    print(f"Result set for match {match['team1']} vs {match['team2']}:")
    print(f"{match['team1']} {home_goals} - {away_goals} {match['team2']}")
    
    if match.get("is_knockout", False) and "resolution_type" in match["result"]:
        resolution_text = {
            "FT": "Full Time",
            "ET": "Extra Time",
            "PEN": "Penalties"
        }[match["result"]["resolution_type"]]
        print(f"Resolution: {resolution_text}")

def show_all_predictions():
    """Show all predictions for all users."""
    print("\n=== ALL USER PREDICTIONS ===")
    
    predictions = get_all_predictions()
    matches = get_all_matches()
    users = get_all_users()
    
    for user_id, user_predictions in predictions.items():
        user = users.get(user_id, {"first_name": "Unknown", "username": ""})
        
        print(f"\nUser: {user.get('first_name')} (@{user.get('username')})")
        
        for match_id, prediction in user_predictions.items():
            match = matches.get(match_id)
            if not match:
                continue
            
            pred_text = f"{prediction['home_goals']}-{prediction['away_goals']}"
            
            if match.get("is_knockout", False) and "resolution_type" in prediction:
                pred_text += f" ({prediction['resolution_type']})"
            
            print(f"• {match['team1']} vs {match['team2']}: {pred_text}")

def main():
    """Run the test script."""
    print("=== Club World Cup 2025 Prediction Bot Test ===")
    print("This script will populate your Firebase database with test data.")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    # Clear existing data
    print("Clearing existing Firebase data...")
    clear_all_data()
    
    # Create test data
    users = create_test_users()
    matches = create_test_matches()
    predictions = create_test_predictions(users, matches)
    
    # Calculate scores
    calculate_scores(predictions, matches)
    
    # Display leaderboard
    display_leaderboard()
    
    # Simulate user prediction
    simulate_match_prediction()
    
    # Simulate setting result
    simulate_setting_result()
    
    # Recalculate scores after new result
    calculate_scores(get_all_predictions(), get_all_matches())
    
    # Display updated leaderboard
    display_leaderboard()
    
    # Show all predictions
    show_all_predictions()
    
    print("\nTest completed! You can now run the bot with this test data.")
    print("To start the bot, run: python run_bot.py")

if __name__ == "__main__":
    main() 