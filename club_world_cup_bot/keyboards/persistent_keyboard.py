"""
Persistent keyboards for bot users.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_user_keyboard():
    """Generate a persistent keyboard for regular users."""
    keyboard = [
        [KeyboardButton(text="⚽ Matches")],
        [KeyboardButton(text="📋 My Predictions"), KeyboardButton(text="🏆 Leaderboard")],
        [KeyboardButton(text="🥇 My Rank"), KeyboardButton(text="❓ Help")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        persistent=True
    )

def get_admin_keyboard():
    """Generate a persistent keyboard for admin users."""
    keyboard = [
        [KeyboardButton(text="⚽ Matches")],
        [KeyboardButton(text="📋 My Predictions"), KeyboardButton(text="🏆 Leaderboard")],
        [KeyboardButton(text="🥇 My Rank"), KeyboardButton(text="❓ Help")],
        # Admin commands
        [KeyboardButton(text="⚙️ Admin Panel"), KeyboardButton(text="🔄 Update Scores")],
        [KeyboardButton(text="📊 Export CSV"), KeyboardButton(text="📁 View Exports")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        persistent=True
    ) 