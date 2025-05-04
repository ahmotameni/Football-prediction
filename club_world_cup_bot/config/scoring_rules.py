"""
Scoring rules for the Club World Cup 2025 prediction bot.
These can be modified as needed.
"""

SCORING_RULES = {
    # Points for predicting correct winner
    "CORRECT_WINNER": 2,
    
    # Points for predicting correct goal difference
    "CORRECT_GOAL_DIFF": 1,
    
    # Points for predicting exact score
    "EXACT_SCORE": 2,
    
    # Points for predicting correct resolution type (knockout stage only)
    "CORRECT_RESOLUTION_TYPE": 1,
    
    # Points for completely wrong prediction
    "WRONG_PREDICTION": -1
} 