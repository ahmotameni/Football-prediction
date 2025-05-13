"""
Staged Testing for the Club World Cup 2025 Prediction Bot.

This script creates test data for specific tournament stages and allows simulating
different points in time during the tournament.

Available stages:
1. PRE_TOURNAMENT: All matches available for predictions
2. PREDICTIONS_MADE: Multiple users have made predictions, no games played
3. FIRST_DAY: First day completed with some results, scores calculated
4. TOURNAMENT_END: All games finished with results

Usage:
    python staged_test.py [stage_number] [--reload]
    
    If stage_number is provided, the environment will be set to that stage.
    If --reload is provided, it will completely reload data from stored stage snapshots.
    Otherwise, the environment will transition to that stage keeping current predictions.
"""
import os
import sys
import json
import datetime
import random
import shutil
from datetime import timedelta

# Ensure we're in the correct directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Define paths
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
STAGE_DATA_DIR = os.path.join(SCRIPT_DIR, 'stage_data')
PREDICTIONS_FILE = os.path.join(DATA_DIR, 'predictions.json')
MATCHES_FILE = os.path.join(DATA_DIR, 'matches.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
CURRENT_STAGE_FILE = os.path.join(DATA_DIR, 'current_stage.json')

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STAGE_DATA_DIR, exist_ok=True)

# Stage definitions
STAGES = {
    1: "PRE_TOURNAMENT",
    2: "PREDICTIONS_MADE",
    3: "FIRST_DAY",
    4: "TOURNAMENT_END"
}

# Flag to force recreate stage data
FORCE_RECREATE_STAGES = True

def update_match_years(matches, target_year="2025"):
    """Update match years to the target year."""
    updated = False
    for match_id in matches:
        if "time" in matches[match_id]:
            time_str = matches[match_id]["time"]
            current_year = time_str[:4]
            if current_year != target_year:
                matches[match_id]["time"] = f"{target_year}{time_str[4:]}"
                updated = True
    
    return matches, updated

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

def backup_data():
    """Backup existing data files."""
    print("Backing up current data...")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(SCRIPT_DIR, f'data_backup_{timestamp}')
    
    if os.path.exists(DATA_DIR):
        shutil.copytree(DATA_DIR, backup_dir)
        print(f"Data backed up to {backup_dir}")

def create_test_users():
    """Create test users including the admin from credentials.env."""
    print("Creating test users...")
    
    # Try to get admin username from credentials.env
    admin_username = "Ahmotameni1"  # Default from provided file
    
    # Create users
    users = {
        "54227407": {
            "username": "Ahmotameni",
            "first_name": "AmirHossein",
            "last_name": "Motameni",
            "registered_at": "2025-05-10T00:54:42.029415",
            "is_admin": False
        },
        "123456789": {
            "username": admin_username,
            "first_name": "Admin",
            "last_name": "User",
            "registered_at": datetime.datetime.now().isoformat(),
            "is_admin": True
        },
        "987654321": {
            "username": "regular_user",
            "first_name": "Regular",
            "last_name": "User",
            "registered_at": datetime.datetime.now().isoformat(),
            "is_admin": False
        }
    }
    
    # Add 10 more random users as requested
    for i in range(1, 11):
        user_id = str(random.randint(100000000, 999999999))
        users[user_id] = {
            "username": f"user_{i}",
            "first_name": f"User {i}",
            "last_name": f"Last{i}",
            "registered_at": datetime.datetime.now().isoformat(),
            "is_admin": False
        }
    
    save_json(USERS_FILE, users)
    print(f"Created {len(users)} test users.")
    return users

def prepare_stage_1():
    """Stage 1: PRE_TOURNAMENT - All matches available for predictions."""
    print("\n=== SETTING UP STAGE 1: PRE_TOURNAMENT ===")
    
    # Load matches from the matches.json file
    matches = load_json(MATCHES_FILE)
    
    # Update years to 2025
    matches, year_updated = update_match_years(matches)
    if year_updated:
        print("Updated match years to 2025")
    
    # Make sure no match is locked or has results
    for match_id in matches:
        if "locked" in matches[match_id]:
            matches[match_id]["locked"] = False
        if "result" in matches[match_id]:
            del matches[match_id]["result"]
    
    save_json(MATCHES_FILE, matches)
    
    # Create users
    users = create_test_users()
    
    # No predictions yet in this stage
    save_json(PREDICTIONS_FILE, {})
    
    # Save current stage
    save_json(CURRENT_STAGE_FILE, {"current_stage": 1})
    
    # Save stage data
    stage_dir = os.path.join(STAGE_DATA_DIR, "stage1")
    os.makedirs(stage_dir, exist_ok=True)
    
    shutil.copy(MATCHES_FILE, os.path.join(stage_dir, "matches.json"))
    shutil.copy(USERS_FILE, os.path.join(stage_dir, "users.json"))
    shutil.copy(PREDICTIONS_FILE, os.path.join(stage_dir, "predictions.json"))
    shutil.copy(CURRENT_STAGE_FILE, os.path.join(stage_dir, "current_stage.json"))
    
    print("Stage 1 setup complete. All matches are available for prediction.")
    return matches, users

def prepare_stage_2(matches, users):
    """Stage 2: PREDICTIONS_MADE - Multiple users have made predictions, no games played."""
    print("\n=== SETTING UP STAGE 2: PREDICTIONS_MADE ===")
    
    predictions = {}
    
    # For each user, generate predictions for most matches
    for user_id in users:
        user_predictions = {}
        
        # Each user predicts 80-100% of matches
        predict_count = int(len(matches) * (0.8 + random.random() * 0.2))
        match_ids = list(matches.keys())
        random.shuffle(match_ids)
        
        for i in range(predict_count):
            match_id = match_ids[i]
            
            # Generate prediction
            home_goals = random.randint(0, 5)
            away_goals = random.randint(0, 4)
            
            prediction = {
                "home_goals": home_goals,
                "away_goals": away_goals
            }
            
            # Add resolution type for knockout matches
            if matches[match_id].get("is_knockout", False):
                resolution_types = ["FT", "ET", "PEN"]
                prediction["resolution_type"] = random.choice(resolution_types)
            
            user_predictions[match_id] = prediction
        
        predictions[user_id] = user_predictions
    
    # Save predictions
    save_json(PREDICTIONS_FILE, predictions)
    
    # Save current stage
    save_json(CURRENT_STAGE_FILE, {"current_stage": 2})
    
    # Save stage data
    stage_dir = os.path.join(STAGE_DATA_DIR, "stage2")
    os.makedirs(stage_dir, exist_ok=True)
    
    shutil.copy(MATCHES_FILE, os.path.join(stage_dir, "matches.json"))
    shutil.copy(USERS_FILE, os.path.join(stage_dir, "users.json"))
    shutil.copy(PREDICTIONS_FILE, os.path.join(stage_dir, "predictions.json"))
    shutil.copy(CURRENT_STAGE_FILE, os.path.join(stage_dir, "current_stage.json"))
    
    print(f"Stage 2 setup complete. {len(users)} users have made predictions.")
    
    return predictions

def prepare_stage_3(matches, users, predictions):
    """Stage 3: FIRST_DAY - First day completed with some results."""
    print("\n=== SETTING UP STAGE 3: FIRST_DAY ===")
    
    # Lock matches and add results for the first day (June 15)
    first_day_matches = []
    
    for match_id, match in matches.items():
        match_time = match.get("time", "")
        if match_time[5:10] == "06-15":  # Match the day regardless of year
            first_day_matches.append(match_id)
            
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
    
    # Save updated matches
    save_json(MATCHES_FILE, matches)
    
    # Calculate scores
    calculate_scores(predictions, matches, users)
    
    # Save current stage
    save_json(CURRENT_STAGE_FILE, {"current_stage": 3})
    
    # Save stage data
    stage_dir = os.path.join(STAGE_DATA_DIR, "stage3")
    os.makedirs(stage_dir, exist_ok=True)
    
    shutil.copy(MATCHES_FILE, os.path.join(stage_dir, "matches.json"))
    shutil.copy(USERS_FILE, os.path.join(stage_dir, "users.json"))
    shutil.copy(PREDICTIONS_FILE, os.path.join(stage_dir, "predictions.json"))
    shutil.copy(CURRENT_STAGE_FILE, os.path.join(stage_dir, "current_stage.json"))
    
    print(f"Stage 3 setup complete. {len(first_day_matches)} matches from first day have results.")

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
    
    # Save updated matches
    save_json(MATCHES_FILE, matches)
    
    # Calculate scores
    calculate_scores(predictions, matches, users)
    
    # Save current stage
    save_json(CURRENT_STAGE_FILE, {"current_stage": 4})
    
    # Save stage data
    stage_dir = os.path.join(STAGE_DATA_DIR, "stage4")
    os.makedirs(stage_dir, exist_ok=True)
    
    shutil.copy(MATCHES_FILE, os.path.join(stage_dir, "matches.json"))
    shutil.copy(USERS_FILE, os.path.join(stage_dir, "users.json"))
    shutil.copy(PREDICTIONS_FILE, os.path.join(stage_dir, "predictions.json"))
    shutil.copy(CURRENT_STAGE_FILE, os.path.join(stage_dir, "current_stage.json"))
    
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
    
    save_json(USERS_FILE, users)
    print("Scores calculated and saved.")

def display_leaderboard():
    """Display the current leaderboard."""
    print("\n=== LEADERBOARD ===")
    
    users = load_json(USERS_FILE)
    
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

def get_current_stage():
    """Get the current stage from the stage file."""
    stage_data = load_json(CURRENT_STAGE_FILE, {"current_stage": 1})
    return stage_data.get("current_stage", 1)

def transition_to_stage(target_stage):
    """
    Transition from current stage to target stage without reloading data.
    This keeps all current data and only applies changes needed for the target stage.
    """
    current_stage = get_current_stage()
    
    if current_stage == target_stage:
        print(f"Already at stage {target_stage}: {STAGES[target_stage]}")
        return True
    
    print(f"\n=== TRANSITIONING FROM STAGE {current_stage} TO STAGE {target_stage} ===")
    print(f"Current: {STAGES[current_stage]} → Target: {STAGES[target_stage]}")
    
    # Load current data
    matches = load_json(MATCHES_FILE)
    users = load_json(USERS_FILE)
    predictions = load_json(PREDICTIONS_FILE)
    
    # Update years to 2025 (needed for any stage)
    matches, year_updated = update_match_years(matches)
    if year_updated:
        print("Updated match years to 2025")
        save_json(MATCHES_FILE, matches)
    
    # Moving forward in stages
    if target_stage > current_stage:
        # Stage 1 → 2: Nothing to do, just updating the stage marker
        if current_stage == 1 and target_stage == 2:
            print("Transitioning to PREDICTIONS_MADE stage")
            # User predictions should already exist, just update the stage marker
        
        # Stage 2 → 3: Add first day results
        elif current_stage == 2 and target_stage == 3:
            print("Transitioning to FIRST_DAY stage")
            # Add results for first day matches
            first_day_matches = []
            for match_id, match in matches.items():
                match_time = match.get("time", "")
                if match_time[5:10] == "06-15":  # Match the day regardless of year
                    first_day_matches.append(match_id)
                    
                    # Add result if no result exists
                    if "result" not in match:
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
            
            print(f"Added results for {len(first_day_matches)} first day matches")
            save_json(MATCHES_FILE, matches)
            
            # Calculate scores
            calculate_scores(predictions, matches, users)
        
        # Stage 3 → 4: Add all remaining results
        elif current_stage == 3 and target_stage == 4:
            print("Transitioning to TOURNAMENT_END stage")
            # Add results for all remaining matches
            remaining_matches = 0
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
                remaining_matches += 1
            
            print(f"Added results for {remaining_matches} remaining matches")
            save_json(MATCHES_FILE, matches)
            
            # Calculate scores
            calculate_scores(predictions, matches, users)
        
        # Going too many stages at once
        else:
            print(f"Transitioning multiple stages: {current_stage} → {target_stage}")
            # Process intermediate stages
            for intermediate_stage in range(current_stage + 1, target_stage + 1):
                transition_to_stage(intermediate_stage)
                return True
    
    # Moving backward in stages
    else:
        # Stage 4 → 3: Remove results for matches after first day
        if current_stage == 4 and target_stage == 3:
            print("Transitioning back to FIRST_DAY stage")
            # Keep only first day results, remove the rest
            removed_results = 0
            for match_id, match in matches.items():
                match_time = match.get("time", "")
                if match_time[5:10] != "06-15" and "result" in match:  # Not first day
                    del match["result"]
                    if "locked" in match:
                        match["locked"] = False
                    removed_results += 1
            
            print(f"Removed results for {removed_results} matches after first day")
            save_json(MATCHES_FILE, matches)
            
            # Recalculate scores
            calculate_scores(predictions, matches, users)
        
        # Stage 3 → 2: Remove all results
        elif current_stage == 3 and target_stage == 2:
            print("Transitioning back to PREDICTIONS_MADE stage")
            # Remove all results
            removed_results = 0
            for match_id, match in matches.items():
                if "result" in match:
                    del match["result"]
                    removed_results += 1
                
                if "locked" in match:
                    match["locked"] = False
            
            print(f"Removed results for {removed_results} matches")
            save_json(MATCHES_FILE, matches)
            
            # Reset scores to 0
            for user_id in users:
                if "score" in users[user_id]:
                    users[user_id]["score"] = 0
            
            save_json(USERS_FILE, users)
        
        # Stage 2 → 1: Remove all predictions
        elif current_stage == 2 and target_stage == 1:
            print("Transitioning back to PRE_TOURNAMENT stage")
            # Save an empty predictions file
            save_json(PREDICTIONS_FILE, {})
            
            # Reset scores to 0
            for user_id in users:
                if "score" in users[user_id]:
                    users[user_id]["score"] = 0
            
            save_json(USERS_FILE, users)
        
        # Going too many stages backward
        else:
            print(f"Transitioning multiple stages back: {current_stage} → {target_stage}")
            # Process intermediate stages
            for intermediate_stage in range(current_stage - 1, target_stage - 1, -1):
                transition_to_stage(intermediate_stage)
                return True
    
    # Update current stage marker
    save_json(CURRENT_STAGE_FILE, {"current_stage": target_stage})
    print(f"Successfully transitioned to stage {target_stage}: {STAGES[target_stage]}")
    display_leaderboard()
    return True

def load_stage(stage_number, force_reload=False):
    """Load data from a specific stage."""
    if stage_number < 1 or stage_number > 4:
        print(f"Invalid stage number. Please use 1-4.")
        return False
    
    current_stage = get_current_stage()
    
    # If we're using force_reload or creating stages for the first time
    if force_reload or FORCE_RECREATE_STAGES:
        stage_dir = os.path.join(STAGE_DATA_DIR, f"stage{stage_number}")
        
        # If we need to create the stages
        if FORCE_RECREATE_STAGES or not os.path.exists(stage_dir):
            print(f"Stage {stage_number} data not found or force recreate is enabled. Creating all stages...")
            create_all_stages()
        
        print(f"\n=== LOADING STAGE {stage_number}: {STAGES[stage_number]} ===")
        
        # Copy stage files to data directory
        shutil.copy(os.path.join(stage_dir, "matches.json"), MATCHES_FILE)
        shutil.copy(os.path.join(stage_dir, "users.json"), USERS_FILE)
        shutil.copy(os.path.join(stage_dir, "predictions.json"), PREDICTIONS_FILE)
        shutil.copy(os.path.join(stage_dir, "current_stage.json"), CURRENT_STAGE_FILE)
        
        # Verify years are correct in the matches file
        matches = load_json(MATCHES_FILE)
        matches, year_updated = update_match_years(matches)
        if year_updated:
            print("Updated match years to 2025")
            save_json(MATCHES_FILE, matches)
        
        print(f"Stage {stage_number} loaded. You can now run the bot to test this stage.")
        display_leaderboard()
        return True
    
    # If we're transitioning between stages
    else:
        return transition_to_stage(stage_number)

def create_all_stages():
    """Create all stages from scratch."""
    # Backup current data
    backup_data()
    
    # Create stage data
    matches, users = prepare_stage_1()
    predictions = prepare_stage_2(matches, users)
    prepare_stage_3(matches, users, predictions)
    prepare_stage_4(matches, users, predictions)
    
    print("\n=== ALL STAGES CREATED ===")

def main():
    """Run the staged test creation."""
    print("=== Club World Cup 2025 Prediction Bot Staged Test ===")
    
    # Check if we're loading a specific stage
    if len(sys.argv) > 1:
        try:
            stage_number = int(sys.argv[1])
            
            # Check for --reload flag
            force_reload = "--reload" in sys.argv
            
            if load_stage(stage_number, force_reload):
                print(f"\nStage {stage_number} loaded. Run your bot to test this stage.")
                if force_reload:
                    print("Note: Data was completely reloaded from stage snapshots.")
                else:
                    print("Note: Current data was preserved and transitioned to the new stage.")
                print("To run the bot: python run_bot.py")
            return
        except ValueError:
            print("Invalid stage number. Please provide a number 1-4.")
            return
    
    # Create all stages
    print("This script will create test data for all tournament stages.")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    create_all_stages()
    
    print("You can now load any stage using:")
    print("  python staged_test.py [stage_number]")
    print("  Add --reload to reset the stage completely instead of transitioning")
    print("\nWhere stage_number is:")
    print("  1: Before the tournament starts (all matches available for prediction)")
    print("  2: Users made predictions, but no games played yet")
    print("  3: First day completed, some matches have results")
    print("  4: Tournament finished, all matches have results")
    
    # Show the final leaderboard
    display_leaderboard()

if __name__ == "__main__":
    main() 