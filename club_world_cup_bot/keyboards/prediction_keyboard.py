"""
Inline keyboards for match predictions.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_matches_keyboard(matches):
    """Generate a keyboard with available matches to predict."""
    kb = InlineKeyboardBuilder()
    
    for match_id, match in matches.items():
        if not match.get("locked", False):
            button_text = f"{match['team1']} vs {match['team2']} - {match['time']}"
            kb.button(text=button_text, callback_data=f"match_{match_id}")
    
    return kb.adjust(1).as_markup()

def get_home_goals_keyboard(match_id):
    """Generate a keyboard for selecting home team goals."""
    kb = InlineKeyboardBuilder()
    
    # Goals from 0 to 9
    for i in range(10):
        kb.button(text=str(i), callback_data=f"home_{match_id}_{i}")
    
    return kb.adjust(5).as_markup()

def get_away_goals_keyboard(match_id, home_goals):
    """Generate a keyboard for selecting away team goals."""
    kb = InlineKeyboardBuilder()
    
    # Goals from 0 to 9
    for i in range(10):
        kb.button(text=str(i), callback_data=f"away_{match_id}_{home_goals}_{i}")
    
    return kb.adjust(5).as_markup()

def get_resolution_type_keyboard(match_id, home_goals, away_goals):
    """Generate a keyboard for selecting resolution type (knockout matches only)."""
    kb = InlineKeyboardBuilder()
    
    resolution_types = [
        ("Full Time", "FT"),
        ("Extra Time", "ET"),
        ("Penalties", "PEN")
    ]
    
    for text, value in resolution_types:
        kb.button(
            text=text, 
            callback_data=f"resolution_{match_id}_{home_goals}_{away_goals}_{value}"
        )
    
    return kb.adjust(1).as_markup()

def get_admin_keyboard():
    """Generate the admin panel keyboard."""
    kb = InlineKeyboardBuilder()
    
    buttons = [
        ("Add Match", "admin_addmatch"),
        ("Set Result", "admin_setresult"),
        ("Update Leaderboard", "admin_updateleaderboard"),
        ("Export CSV", "admin_exportcsv")
    ]
    
    for text, callback_data in buttons:
        kb.button(text=text, callback_data=callback_data)
    
    return kb.adjust(1).as_markup()

def get_match_list_keyboard(matches, is_admin=False):
    """Generate a keyboard with all matches (for viewing or admin actions)."""
    kb = InlineKeyboardBuilder()
    
    for match_id, match in matches.items():
        prefix = "adminmatch_" if is_admin else "viewmatch_"
        status = "✅" if "result" in match else "⏳"
        button_text = f"{status} {match['team1']} vs {match['team2']} - {match['time']}"
        kb.button(text=button_text, callback_data=f"{prefix}{match_id}")
    
    return kb.adjust(1).as_markup()

def get_enhanced_matches_keyboard(matches, user_predictions=None):
    """
    Generate an enhanced keyboard showing matches with prediction status and results.
    
    Args:
        matches (dict): Dictionary of matches
        user_predictions (dict, optional): Dictionary of user predictions
        
    Returns:
        InlineKeyboardMarkup: Keyboard markup
    """
    kb = InlineKeyboardBuilder()
    user_predictions = user_predictions or {}
    
    for match_id, match in matches.items():
        # Determine match status
        is_locked = match.get("locked", False)
        has_result = "result" in match
        has_prediction = match_id in user_predictions
        
        # Choose appropriate emoji based on status
        if has_result:
            # Completed match
            emoji = "✅ "
            callback = f"viewresult_{match_id}"
        elif is_locked:
            # Locked but no result yet
            emoji = "🔒 "
            callback = f"viewmatch_{match_id}"
        elif has_prediction:
            # User has predicted this match
            emoji = "🔮 "
            callback = f"match_{match_id}"
        else:
            # Open for prediction
            emoji = "⚽ "
            callback = f"match_{match_id}"
        
        # Format time to be more readable
        match_time = match['time']
        
        # Create button text with prediction info if available
        button_text = f"{emoji}{match['team1']} vs {match['team2']} - {match_time}"
        
        # Add prediction info if user has predicted
        if has_prediction:
            pred = user_predictions[match_id]
            pred_text = f"{pred['home_goals']}-{pred['away_goals']}"
            
            if match.get("is_knockout", False) and "resolution_type" in pred:
                res_short = {"FT": "FT", "ET": "ET", "PEN": "P"}
                pred_text += f" ({res_short.get(pred['resolution_type'], pred['resolution_type'])})"
            
            button_text += f" [{pred_text}]"
        
        kb.button(text=button_text, callback_data=callback)
    
    return kb.adjust(1).as_markup() 