"""
Command handlers for admin users.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from datetime import datetime

from club_world_cup_bot.messages.strings import (
    ADMIN_PANEL, ADMIN_ONLY, MATCH_ADDED, 
    RESULT_SET, LEADERBOARD_UPDATED, CSV_EXPORTED
)
from club_world_cup_bot.keyboards.prediction_keyboard import (
    get_admin_keyboard as get_admin_inline_keyboard, get_match_list_keyboard
)
from club_world_cup_bot.keyboards.persistent_keyboard import (
    get_admin_keyboard as get_admin_reply_keyboard
)
from club_world_cup_bot.services.prediction import (
    is_admin, is_admin_by_username, add_match, set_match_result, get_matches
)
from club_world_cup_bot.services.scoring import update_leaderboard
from club_world_cup_bot.services.export_csv import export_predictions_csv

# Optional API Football integration
try:
    from club_world_cup_bot.services.api_fetch import APIFootballClient, format_match_data
    API_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    API_AVAILABLE = False

router = Router()

class AddMatchForm(StatesGroup):
    """States for adding a match."""
    team1 = State()
    team2 = State()
    time = State()
    is_knockout = State()

class SetResultForm(StatesGroup):
    """States for setting match result."""
    match_id = State()
    home_goals = State()
    away_goals = State()
    resolution_type = State()
    knockout_winner = State()

# Removed ExportedFilesForm as it's no longer needed with Firebase

def check_admin_permissions(user):
    """Check if user has admin permissions by ID or username."""
    user_id = str(user.id)
    username = user.username
    
    # First check by ID, then by username if available
    if is_admin(user_id):
        return True
    
    if username and is_admin_by_username(username):
        return True
    
    return False

# Button handlers for admin-specific buttons
@router.message(F.text == "⚙️ Admin Panel")
async def button_admin(message: Message):
    """Handle the Admin Panel button."""
    await cmd_admin(message)

@router.message(F.text == "🔄 Update Scores")
async def button_update_leaderboard(message: Message):
    """Handle the Update Scores button."""
    if not check_admin_permissions(message.from_user):
        await message.answer(ADMIN_ONLY)
        return
    
    update_leaderboard()
    await message.answer(LEADERBOARD_UPDATED)

@router.message(F.text == "📊 Export CSV")
async def button_export_csv(message: Message):
    """Handle the Export CSV button."""
    if not check_admin_permissions(message.from_user):
        await message.answer(ADMIN_ONLY)
        return
    
    csv_data, filename = export_predictions_csv()
    
    # Send as document
    from io import BytesIO
    document = BytesIO(csv_data.encode('utf-8'))
    await message.answer_document(
        document=document,
        filename=filename,
        caption=CSV_EXPORTED
    )

@router.message(F.text == "📁 View Exports")
async def button_exported_files(message: Message, state: FSMContext):
    """Handle the View Exports button."""
    await message.answer("Export functionality has been simplified. Use 'Export CSV' to generate and download a new export file.")

# Original command handlers
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Handle the /admin command."""
    if not check_admin_permissions(message.from_user):
        await message.answer(ADMIN_ONLY)
        return
    
    # Send admin panel with inline keyboard for specific admin actions
    inline_keyboard = get_admin_inline_keyboard()
    
    # Ensure the user has the admin reply keyboard
    reply_keyboard = get_admin_reply_keyboard()
    
    await message.answer(
        ADMIN_PANEL, 
        reply_markup=inline_keyboard
    )

@router.callback_query(F.data == "admin_addmatch")
async def process_add_match(callback: CallbackQuery, state: FSMContext):
    """Handle add match button click."""
    await callback.answer()
    
    if not check_admin_permissions(callback.from_user):
        await callback.message.edit_text(ADMIN_ONLY)
        return
    
    await state.set_state(AddMatchForm.team1)
    await callback.message.edit_text("Enter the home team name:")

@router.callback_query(F.data == "admin_setresult")
async def process_set_result(callback: CallbackQuery, state: FSMContext):
    """Handle set result button click."""
    await callback.answer()
    
    if not check_admin_permissions(callback.from_user):
        await callback.message.edit_text(ADMIN_ONLY)
        return
    
    matches = get_matches()
    if not matches:
        await callback.message.edit_text("No matches available.")
        return
    
    keyboard = get_match_list_keyboard(matches, is_admin=True)
    await callback.message.edit_text(
        "Select a match to set the result:",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "admin_updateleaderboard")
async def process_update_leaderboard(callback: CallbackQuery):
    """Handle update leaderboard button click."""
    await callback.answer()
    
    if not check_admin_permissions(callback.from_user):
        await callback.message.edit_text(ADMIN_ONLY)
        return
    
    update_leaderboard()
    await callback.message.edit_text(LEADERBOARD_UPDATED)

@router.callback_query(F.data == "admin_exportcsv")
async def process_export_csv(callback: CallbackQuery):
    """Handle export CSV button click."""
    await callback.answer()
    
    if not check_admin_permissions(callback.from_user):
        await callback.message.edit_text(ADMIN_ONLY)
        return
    
    csv_data, filename = export_predictions_csv()
    
    # Send as document
    from io import BytesIO
    document = BytesIO(csv_data.encode('utf-8'))
    await callback.message.answer_document(
        document=document,
        filename=filename,
        caption=CSV_EXPORTED
    )

@router.message(AddMatchForm.team1)
async def process_team1(message: Message, state: FSMContext):
    """Handle team1 input."""
    await state.update_data(team1=message.text)
    await state.set_state(AddMatchForm.team2)
    await message.answer("Enter the away team name:")

@router.message(AddMatchForm.team2)
async def process_team2(message: Message, state: FSMContext):
    """Handle team2 input."""
    await state.update_data(team2=message.text)
    await state.set_state(AddMatchForm.time)
    await message.answer(
        "Enter the match date and time in format YYYY-MM-DD HH:MM:"
    )

@router.message(AddMatchForm.time)
async def process_time(message: Message, state: FSMContext):
    """Handle time input."""
    # Validate time format
    try:
        datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await state.update_data(time=message.text)
        await state.set_state(AddMatchForm.is_knockout)
        await message.answer(
            "Is this a knockout stage match? (yes/no):"
        )
    except ValueError:
        await message.answer(
            "Invalid format. Please enter the time in format YYYY-MM-DD HH:MM:"
        )

@router.message(AddMatchForm.is_knockout)
async def process_is_knockout(message: Message, state: FSMContext):
    """Handle is_knockout input."""
    is_knockout = message.text.lower() in ("yes", "y", "true", "1")
    
    data = await state.get_data()
    team1 = data["team1"]
    team2 = data["team2"]
    time = data["time"]
    
    # Add the match
    match_id = add_match(team1, team2, time, is_knockout)
    
    await state.clear()
    await message.answer(
        f"{MATCH_ADDED}\n\n"
        f"Match ID: {match_id}\n"
        f"Teams: {team1} vs {team2}\n"
        f"Time: {time}\n"
        f"Knockout: {'Yes' if is_knockout else 'No'}"
    )

@router.callback_query(F.data.startswith("adminmatch_"))
async def process_admin_match_selection(callback: CallbackQuery, state: FSMContext):
    """Handle match selection for setting result."""
    await callback.answer()
    
    match_id = callback.data.split("_")[1]
    matches = get_matches()
    match = matches.get(match_id)
    
    if not match:
        await callback.message.edit_text("Match not found.")
        return
    
    await state.update_data(match_id=match_id)
    await state.set_state(SetResultForm.home_goals)
    
    await callback.message.edit_text(
        f"Setting result for {match['team1']} vs {match['team2']}.\n"
        f"Enter goals for {match['team1']}:"
    )

@router.message(SetResultForm.home_goals)
async def process_result_home_goals(message: Message, state: FSMContext):
    """Handle home goals input for result."""
    try:
        home_goals = int(message.text)
        if home_goals < 0:
            raise ValueError("Goals must be positive")
        
        await state.update_data(home_goals=home_goals)
        await state.set_state(SetResultForm.away_goals)
        
        data = await state.get_data()
        match_id = data["match_id"]
        matches = get_matches()
        match = matches.get(match_id)
        
        await message.answer(f"Enter goals for {match['team2']}:")
    except ValueError:
        await message.answer("Please enter a valid number:")

@router.message(SetResultForm.away_goals)
async def process_result_away_goals(message: Message, state: FSMContext):
    """Handle away goals input for result."""
    try:
        away_goals = int(message.text)
        if away_goals < 0:
            raise ValueError("Goals must be positive")
        
        await state.update_data(away_goals=away_goals)
        
        data = await state.get_data()
        match_id = data["match_id"]
        home_goals = data["home_goals"]
        matches = get_matches()
        match = matches.get(match_id)
        
        if match.get("is_knockout", False):
            # For knockout matches check if it's a tie
            if home_goals == away_goals:
                # If it's a tie, we need both resolution type and winner
                await state.set_state(SetResultForm.resolution_type)
                await message.answer(
                    "Match ended in a tie. How was it decided? Enter one of: "
                    "ET (Extra Time), PEN (Penalties):"
                )
            else:
                # If not a tie, set as FT with appropriate winner
                winner = "1" if home_goals > away_goals else "2"
                resolution_type = f"FT_{winner}"
                set_match_result(match_id, home_goals, away_goals, resolution_type)
                await state.clear()
                
                winner_name = match['team1'] if winner == "1" else match['team2']
                await message.answer(
                    f"{RESULT_SET}\n\n"
                    f"Match: {match['team1']} vs {match['team2']}\n"
                    f"Result: {home_goals}-{away_goals} ({winner_name} wins in Full Time)\n\n"
                    f"{LEADERBOARD_UPDATED}"
                )
        else:
            # For group stage matches, set the result immediately
            set_match_result(match_id, home_goals, away_goals)
            await state.clear()
            
            await message.answer(
                f"{RESULT_SET}\n\n"
                f"Match: {match['team1']} vs {match['team2']}\n"
                f"Result: {home_goals}-{away_goals}\n\n"
                f"{LEADERBOARD_UPDATED}"
            )
    except ValueError:
        await message.answer("Please enter a valid number:")

@router.message(SetResultForm.resolution_type)
async def process_result_resolution_type(message: Message, state: FSMContext):
    """Handle resolution type input for result."""
    resolution_type = message.text.upper()
    
    if resolution_type not in ("ET", "PEN"):
        await message.answer(
            "Invalid resolution type for tie. Please enter one of: "
            "ET (Extra Time), PEN (Penalties):"
        )
        return
    
    await state.update_data(resolution_type=resolution_type)
    await state.set_state(SetResultForm.knockout_winner)
    
    data = await state.get_data()
    match_id = data["match_id"]
    matches = get_matches()
    match = matches.get(match_id)
    
    await message.answer(
        f"Which team won after the tie?\n"
        f"1. {match['team1']}\n"
        f"2. {match['team2']}\n\n"
        f"Enter 1 or 2:"
    )

@router.message(SetResultForm.knockout_winner)
async def process_knockout_winner(message: Message, state: FSMContext):
    """Handle knockout winner selection."""
    winner = message.text.strip()
    
    if winner not in ("1", "2"):
        await message.answer("Please enter 1 or 2 to select the winner:")
        return
    
    data = await state.get_data()
    match_id = data["match_id"]
    home_goals = data["home_goals"]
    away_goals = data["away_goals"]
    resolution_type = data["resolution_type"]
    
    matches = get_matches()
    match = matches.get(match_id)
    
    # Combine resolution type and winner - handling more complex formats if needed
    full_resolution = f"{resolution_type}_{winner}"
    
    # Set the match result
    set_match_result(match_id, home_goals, away_goals, full_resolution)
    await state.clear()
    
    # Get team name for display
    winner_name = match['team1'] if winner == "1" else match['team2']
    resolution_text = "Extra Time" if resolution_type == "ET" else "Penalties"
    
    await message.answer(
        f"{RESULT_SET}\n\n"
        f"Match: {match['team1']} vs {match['team2']}\n"
        f"Result: {home_goals}-{away_goals} ({winner_name} wins in {resolution_text})\n\n"
        f"{LEADERBOARD_UPDATED}"
    )

@router.message(Command("exportedfiles"))
async def cmd_exported_files(message: Message, state: FSMContext):
    """Handle the /exportedfiles command - simplified for Firebase version."""
    if not check_admin_permissions(message.from_user):
        await message.answer(ADMIN_ONLY)
        return
    
    await message.answer("Export functionality has been simplified. Use the 'Export CSV' command or button to generate and download a new export file directly.") 