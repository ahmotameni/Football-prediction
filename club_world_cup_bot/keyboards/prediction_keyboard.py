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
    
    # If it's a tie, show resolution types with team options
    if int(home_goals) == int(away_goals):
        # Get the match data to show team names
        from club_world_cup_bot.services.prediction import get_matches
        matches = get_matches()
        match = matches.get(match_id, {})
        team1 = match.get('team1', 'Home')
        team2 = match.get('team2', 'Away')
        
        # Offer ET or PEN with team selection
        resolution_teams = [
            (f"{team1} wins in ET", "ET_1"),
            (f"{team2} wins in ET", "ET_2"),
            (f"{team1} wins in PEN", "PEN_1"),
            (f"{team2} wins in PEN", "PEN_2"),
        ]
        
        for text, value in resolution_teams:
            kb.button(
                text=text, 
                callback_data=f"resolution_{match_id}_{home_goals}_{away_goals}_{value}"
            )
    else:
        # If not a tie, just set as FT automatically in the handler
        # This is a placeholder as we'll handle non-ties differently
        kb.button(
            text="Confirm", 
            callback_data=f"resolution_{match_id}_{home_goals}_{away_goals}_FT"
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
        status = "🏁" if "result" in match else "⏳"
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
            emoji = "🏁 "
            callback = f"viewresult_{match_id}"
        elif is_locked:
            # Locked but no result yet
            emoji = "🔒 "
            callback = f"viewmatch_{match_id}"
        elif has_prediction:
            # User has predicted this match
            emoji = "✅ "
            callback = f"match_{match_id}"
        else:
            # Open for prediction
            emoji = "⏳ "
            callback = f"match_{match_id}"
        
        # Format time to be more readable
        match_time = match['time']
        
        # Create button text with prediction info if available
        button_text = f"{emoji}{match['team1']} vs {match['team2']} - {match_time}"
        
        # Add prediction info if user has predicted
        if has_prediction:
            pred = user_predictions[match_id]
            pred_text = f"{pred['home_goals']}-{pred['away_goals']}"
            
            if match.get("is_knockout", False):
                # For knockout matches, add resolution type
                if int(pred['home_goals']) == int(pred['away_goals']):
                    # For ties, display winner with resolution type
                    res_type = pred.get('resolution_type', '')
                    winner_id = pred.get('knockout_winner', '')
                    winner_name = match['team1'][:3] if winner_id == '1' else match['team2'][:3]
                    
                    res_short = {"ET": "ET", "PEN": "P"}
                    if res_type in res_short:
                        pred_text += f" ({winner_name} {res_short.get(res_type)})"
                else:
                    # For non-ties, display FT
                    pred_text += " (FT)"
            
            button_text += f" [{pred_text}]"
        
        kb.button(text=button_text, callback_data=callback)
    
    return kb.adjust(1).as_markup() 