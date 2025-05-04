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