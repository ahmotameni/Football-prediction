"""
Message strings for the Club World Cup 2025 prediction bot.
"""

# General messages
WELCOME_MESSAGE = """
Welcome to the Club World Cup 2025 Prediction Bot! 🏆⚽

Make predictions for upcoming matches and compete with friends and family!

Use the command buttons below to navigate the bot.

Good luck! ⚽🍀
"""

HELP_MESSAGE = """
Available commands:

/start - Start the bot
/predict - Make predictions for upcoming matches
/matches - View upcoming matches
/mypredictions - View your current predictions
/leaderboard - View the current standings
/myrank - See your position in the leaderboard
/help - Show this help message

Admin commands:
/admin - Show admin options
/addmatch - Add a new match
/setresult - Set match result
/updateleaderboard - Recalculate all scores
/exportcsv - Export predictions and scores to CSV
/exportedfiles - View or download exported files
"""

# Prediction messages
PREDICTION_START = "Select a match to predict:"
NO_MATCHES_TO_PREDICT = "There are no upcoming matches to predict at the moment."
PREDICTION_SUCCESS = "Your prediction has been saved! ✅"
PREDICTION_UPDATED = "Your prediction has been updated! ✅"
PREDICTION_LOCKED = "This match is locked and can no longer be predicted."
NO_PREDICTIONS = "You haven't made any predictions yet."

# Match messages
MATCH_LIST_HEADER = "📅 Upcoming Matches:"
NO_UPCOMING_MATCHES = "There are no upcoming matches at the moment."
MATCH_ADDED = "Match added successfully! ✅"
RESULT_SET = "Match result set successfully! ✅"

# Leaderboard messages
LEADERBOARD_HEADER = "🏆 Current Leaderboard:"
EMPTY_LEADERBOARD = "No scores available yet."
RANK_MESSAGE = "Your current rank: #{} with {} points."

# Admin messages
ADMIN_PANEL = """
Admin Panel:

/addmatch - Add a new match
/setresult - Set match result
/updateleaderboard - Recalculate all scores
/exportcsv - Export predictions and scores
/exportedfiles - View or download exported files
"""

ADMIN_ONLY = "This command is only available to admins."
LEADERBOARD_UPDATED = "Leaderboard has been updated! ✅"
CSV_EXPORTED = "CSV file has been exported! ✅"

# Error messages
GENERAL_ERROR = "An error occurred. Please try again later."
INVALID_FORMAT = "Invalid format. Please try again." 