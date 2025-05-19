"""
Scoring rules for the Club World Cup 2025 prediction bot.
These can be modified as needed.
"""

SCORING_RULES = {
    # Points for predicting correct winner
    "CORRECT_WINNER": 1,
    
    # Points for predicting correct goal difference
    "CORRECT_GOAL_DIFF": 1,
    
    # Points for predicting exact score
    "EXACT_SCORE": 1,
    
    # Points for predicting correct resolution type (ET/PEN) and winner for knockout matches after tie
    "CORRECT_RESOLUTION_TYPE": 2,
    
    # Points for completely wrong prediction
    "WRONG_PREDICTION": -1
} 