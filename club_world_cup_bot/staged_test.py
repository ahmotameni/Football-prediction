"""
Staged Testing for the Club World Cup 2025 Prediction Bot.

This script creates test data for specific tournament stages using Firebase Realtime Database.
Each stage represents a different point in time during the tournament.

Available stages:
1. PRE_TOURNAMENT: All matches available for predictions
2. PREDICTIONS_MADE: Multiple users have made predictions, no games played
3. FIRST_DAY: First day completed with some results, scores calculated
4. TOURNAMENT_END: All games finished with results

Usage:
    python staged_test.py [stage_number]
    
    If stage_number is provided, the Firebase database will be set to that stage.
"""
import random
import datetime
from datetime import timedelta

# Import Firebase helpers
from .firebase_helpers import (
    get_all_users, save_user,
    get_all_matches, save_match,
    get_all_predictions, save_prediction,
    get_current_stage, set_current_stage,
    clear_all_data
)

# Stage definitions
STAGES = {
    1: "PRE_TOURNAMENT",
    2: "PREDICTIONS_MADE", 
    3: "FIRST_DAY",
    4: "TOURNAMENT_END"
}

def create_test_users():
    """Create test users including the admin."""
    print("Creating test users...")
    
    admin_username = "Ahmotameni1"  # Default admin username
    
    # Create users
    users = [
        {
            "user_id": "54227407",
            "data": {
                "username": "Ahmotameni",
                "first_name": "AmirHossein",
                "last_name": "Motameni",
                "registered_at": "2025-05-10T00:54:42.029415",
                "is_admin": False,
                "whitelisted": True,
                "score": 0
            }
        },
        {
            "user_id": "123456789",
            "data": {
                "username": admin_username,
                "first_name": "Admin",
                "last_name": "User",
                "registered_at": datetime.datetime.now().isoformat(),
                "is_admin": True,
                "whitelisted": True,
                "score": 0
            }
        },
        {
            "user_id": "987654321",
            "data": {
                "username": "regular_user",
                "first_name": "Regular",
                "last_name": "User",
                "registered_at": datetime.datetime.now().isoformat(),
                "is_admin": False,
                "whitelisted": True,
                "score": 0
            }
        }
    ]
    
    # Add 10 more random users
    for i in range(1, 11):
        user_id = str(random.randint(100000000, 999999999))
        users.append({
            "user_id": user_id,
            "data": {
                "username": f"user_{i}",
                "first_name": f"User {i}",
                "last_name": f"Last{i}",
                "registered_at": datetime.datetime.now().isoformat(),
                "is_admin": False,
                "whitelisted": True,
                "score": 0
            }
        })
    
    # Save users to Firebase
    for user in users:
        save_user(user["user_id"], user["data"])
    
    print(f"Created {len(users)} test users.")
    return {user["user_id"]: user["data"] for user in users}

def create_base_matches():
    """Create base match data for the tournament."""
    print("Creating tournament matches...")
    
    # Club World Cup Teams (16 teams)
    teams = [
        "Manchester City", "Real Madrid", "Bayern Munich", "Flamengo",
        "Al-Ahly", "Auckland City", "Urawa Red Diamonds", "Al-Hilal",
        "Seattle Sounders", "Wydad Casablanca", "Mamelodi Sundowns", "Ulsan Hyundai",
        "Monterrey", "Palmeiras", "Esperance", "Inter Milan"
    ]
    
    now = datetime.datetime.now()
    match_id = 1
    
    # Group stage matches - set to June 15-20, 2025
    base_date = datetime.datetime(2025, 6, 15, 18, 0)
    
    # Group stage (4 groups of 4 teams each)
    for group in range(4):
        group_teams = teams[group*4:(group+1)*4]
        day_offset = 0
        
        # Each team plays each other team in their group
        for i in range(4):
            for j in range(i+1, 4):
                match_time = base_date + timedelta(days=day_offset, hours=random.randint(0, 6))
                
                match_data = {
                    "team1": group_teams[i],
                    "team2": group_teams[j],
                    "time": match_time.strftime("%Y-%m-%d %H:%M"),
                    "is_knockout": False,
                    "locked": False
                }
                
                save_match(str(match_id), match_data)
                match_id += 1
                
                # Space out matches
                if match_id % 4 == 0:
                    day_offset += 1
    
    # Knockout stage - set to later dates
    knockout_teams = teams[:8]  # Top 8 teams qualify
    
    # Quarter-finals
    knockout_date = datetime.datetime(2025, 6, 25, 20, 0)
    for i in range(0, 8, 2):
        match_time = knockout_date + timedelta(days=i//2)
        
        match_data = {
            "team1": knockout_teams[i],
            "team2": knockout_teams[i+1],
            "time": match_time.strftime("%Y-%m-%d %H:%M"),
            "is_knockout": True,
            "locked": False
        }
        
        save_match(str(match_id), match_data)
        match_id += 1
    
    # Semi-finals
    semi_date = datetime.datetime(2025, 6, 29, 20, 0)
    semi_teams = knockout_teams[:4]
    for i in range(0, 4, 2):
        match_time = semi_date + timedelta(days=i//2)
        
        match_data = {
            "team1": semi_teams[i],
            "team2": semi_teams[i+1],
            "time": match_time.strftime("%Y-%m-%d %H:%M"),
            "is_knockout": True,
            "locked": False
        }
        
        save_match(str(match_id), match_data)
        match_id += 1
    
    # Final
    final_date = datetime.datetime(2025, 7, 2, 20, 0)
    final_teams = semi_teams[:2]
    
    match_data = {
        "team1": final_teams[0],
        "team2": final_teams[1],
        "time": final_date.strftime("%Y-%m-%d %H:%M"),
        "is_knockout": True,
        "locked": False
    }
    
    save_match(str(match_id), match_data)
    
    matches = get_all_matches()
    print(f"Created {len(matches)} tournament matches.")
    return matches

def prepare_stage_1():
    """Stage 1: PRE_TOURNAMENT - All matches available for predictions."""
    print("\n=== SETTING UP STAGE 1: PRE_TOURNAMENT ===")
    
    # Clear existing data
    clear_all_data()
    
    # Create users and matches
    users = create_test_users()
    matches = create_base_matches()
    
    # Set current stage
    set_current_stage(1)
    
    print("Stage 1 setup complete. All matches are available for prediction.")
    return matches, users

def prepare_stage_2(matches, users):
    """Stage 2: PREDICTIONS_MADE - Multiple users have made predictions, no games played."""
    print("\n=== SETTING UP STAGE 2: PREDICTIONS_MADE ===")
    
    prediction_count = 0
    
    # For each user, generate predictions for most matches
    for user_id in users:
        # Each user predicts 80-100% of matches
        predict_count = int(len(matches) * (0.8 + random.random() * 0.2))
        match_ids = list(matches.keys())
        random.shuffle(match_ids)
        
        for i in range(predict_count):
            match_id = match_ids[i]
            
            # Generate prediction
            home_goals = random.randint(0, 5)
            away_goals = random.randint(0, 4)
            
            prediction_data = {
                "home_goals": home_goals,
                "away_goals": away_goals
            }
            
            # Add resolution type for knockout matches
            if matches[match_id].get("is_knockout", False):
                resolution_types = ["FT", "ET", "PEN"]
                prediction_data["resolution_type"] = random.choice(resolution_types)
            
            save_prediction(user_id, match_id, prediction_data)
            prediction_count += 1
    
    # Set current stage
    set_current_stage(2)
    
    print(f"Stage 2 setup complete. Created {prediction_count} predictions.")
    return get_all_predictions()

def prepare_stage_3(matches, users, predictions):
    """Stage 3: FIRST_DAY - First day completed with some results."""
    print("\n=== SETTING UP STAGE 3: FIRST_DAY ===")
    
    # Lock matches and add results for the first day (June 15)
    first_day_count = 0
    
    for match_id, match in matches.items():
        match_time = match.get("time", "")
        if match_time[5:10] == "06-15":  # Match the day regardless of year
            first_day_count += 1
            
            # Add result
            home_goals = random.randint(0, 4)
            away_goals = random.randint(0, 3)
            
            match["result"] = {
                "home_goals": home_goals,
                "away_goals": away_goals
            }
            
            # Add resolution type for knockout matches
            if match.get("is_knockout", False):
                resolution_types = ["FT", "ET", "PEN"]
                match["result"]["resolution_type"] = random.choice(resolution_types)
            
            match["locked"] = True
            save_match(match_id, match)
    
    # Calculate scores
    calculate_scores(predictions, matches, users)
    
    # Set current stage
    set_current_stage(3)
    
    print(f"Stage 3 setup complete. {first_day_count} matches from first day have results.")

def prepare_stage_4(matches, users, predictions):
    """Stage 4: TOURNAMENT_END - All games finished with results."""
    print("\n=== SETTING UP STAGE 4: TOURNAMENT_END ===")
    
    # Add results for all matches
    for match_id, match in matches.items():
        # Skip matches that already have results
        if "result" in match:
            continue
            
        # Add result
        home_goals = random.randint(0, 5)
        away_goals = random.randint(0, 4)
        
        match["result"] = {
            "home_goals": home_goals,
            "away_goals": away_goals
        }
        
        # Add resolution type for knockout matches
        if match.get("is_knockout", False):
            resolution_types = ["FT", "ET", "PEN"]
            match["result"]["resolution_type"] = random.choice(resolution_types)
        
        match["locked"] = True
        save_match(match_id, match)
    
    # Calculate scores
    calculate_scores(predictions, matches, users)
    
    # Set current stage
    set_current_stage(4)
    
    print("Stage 4 setup complete. All matches have results.")

def calculate_scores(predictions, matches, users):
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

def load_stage(stage_number):
    """Set up Firebase database for a specific stage."""
    if stage_number < 1 or stage_number > 4:
        print(f"Invalid stage number. Please use 1-4.")
        return False
    
    print(f"\n=== LOADING STAGE {stage_number}: {STAGES[stage_number]} ===")
    
    # Create stage data progressively
    if stage_number >= 1:
        matches, users = prepare_stage_1()
    
    if stage_number >= 2:
        predictions = prepare_stage_2(matches, users)
    
    if stage_number >= 3:
        prepare_stage_3(matches, users, predictions)
    
    if stage_number >= 4:
        prepare_stage_4(matches, users, predictions)
    
    print(f"Stage {stage_number} loaded. You can now run the bot to test this stage.")
    display_leaderboard()
    return True

def main():
    """Run the staged test creation."""
    print("=== Club World Cup 2025 Prediction Bot Staged Test ===")
    
    # Check if we're loading a specific stage
    import sys
    if len(sys.argv) > 1:
        try:
            stage_number = int(sys.argv[1])
            
            if load_stage(stage_number):
                print(f"\nStage {stage_number} loaded. Run your bot to test this stage.")
                print("To run the bot: python run_bot.py")
            return
        except ValueError:
            print("Invalid stage number. Please provide a number 1-4.")
            return
    
    # Show available stages
    print("This script sets up Firebase test data for different tournament stages.")
    print("Usage: python staged_test.py [stage_number]")
    print("\nAvailable stages:")
    for stage_num, stage_name in STAGES.items():
        print(f"  {stage_num}: {stage_name}")
    
    print("\nExample: python staged_test.py 2")
    print("This will set up the Firebase database for stage 2 (PREDICTIONS_MADE)")

if __name__ == "__main__":
    main() 