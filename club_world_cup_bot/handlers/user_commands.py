"""
Command handlers for regular users.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import logging

from club_world_cup_bot.messages.strings import (
    WELCOME_MESSAGE, HELP_MESSAGE, PREDICTION_START, NO_MATCHES_TO_PREDICT,
    PREDICTION_SUCCESS, PREDICTION_UPDATED, PREDICTION_LOCKED, NO_PREDICTIONS,
    MATCH_LIST_HEADER, NO_UPCOMING_MATCHES, LEADERBOARD_HEADER, EMPTY_LEADERBOARD, 
    RANK_MESSAGE
)
from club_world_cup_bot.keyboards.prediction_keyboard import (
    get_matches_keyboard, get_home_goals_keyboard, 
    get_away_goals_keyboard, get_resolution_type_keyboard, 
    get_match_list_keyboard
)
from club_world_cup_bot.keyboards.persistent_keyboard import (
    get_user_keyboard, get_admin_keyboard
)
from club_world_cup_bot.services.prediction import (
    register_user, get_upcoming_matches, get_matches,
    save_prediction, get_user_predictions, is_admin, is_admin_by_username
)
from club_world_cup_bot.services.scoring import get_leaderboard, get_user_rank

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle the /start command."""
    # Register the user
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    register_user(user_id, username, first_name, last_name)
    
    # Check if user is admin
    is_user_admin = is_admin(user_id) or (username and is_admin_by_username(username))
    
    # Send welcome message with appropriate keyboard
    if is_user_admin:
        await message.answer(WELCOME_MESSAGE, reply_markup=get_admin_keyboard())
    else:
        await message.answer(WELCOME_MESSAGE, reply_markup=get_user_keyboard())

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle the /help command."""
    await message.answer(HELP_MESSAGE)

@router.message(F.text == "❓ Help")
async def button_help(message: Message):
    """Handle the Help button."""
    await cmd_help(message)

@router.message(F.text == "🔮 Predict")
async def button_predict(message: Message):
    """Handle the Predict button."""
    await cmd_predict(message)

@router.message(F.text == "📅 Matches")
async def button_matches(message: Message):
    """Handle the Matches button."""
    await cmd_matches(message)

@router.message(F.text == "📋 My Predictions")
async def button_my_predictions(message: Message):
    """Handle the My Predictions button."""
    await cmd_my_predictions(message)

@router.message(F.text == "🏆 Leaderboard")
async def button_leaderboard(message: Message):
    """Handle the Leaderboard button."""
    await cmd_leaderboard(message)

@router.message(F.text == "🥇 My Rank")
async def button_my_rank(message: Message):
    """Handle the My Rank button."""
    await cmd_my_rank(message)

@router.message(Command("predict"))
async def cmd_predict(message: Message):
    """Handle the /predict command."""
    upcoming_matches = get_upcoming_matches()
    
    if not upcoming_matches:
        await message.answer(NO_MATCHES_TO_PREDICT)
        return
    
    keyboard = get_matches_keyboard(upcoming_matches)
    await message.answer(PREDICTION_START, reply_markup=keyboard)

@router.callback_query(F.data.startswith("match_"))
async def process_match_selection(callback: CallbackQuery):
    """Handle match selection for prediction."""
    await callback.answer()
    
    match_id = callback.data.split("_")[1]
    keyboard = get_home_goals_keyboard(match_id)
    
    matches = get_matches()
    match = matches.get(match_id)
    
    if not match:
        await callback.message.edit_text("Match not found.")
        return
    
    if match.get("locked", False):
        await callback.message.edit_text(PREDICTION_LOCKED)
        return
    
    await callback.message.edit_text(
        f"Predict goals for {match['team1']}:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("home_"))
async def process_home_goals(callback: CallbackQuery):
    """Handle home team goals selection."""
    await callback.answer()
    
    _, match_id, home_goals = callback.data.split("_")
    keyboard = get_away_goals_keyboard(match_id, home_goals)
    
    matches = get_matches()
    match = matches.get(match_id)
    
    await callback.message.edit_text(
        f"Selected {home_goals} goals for {match['team1']}.\n"
        f"Now predict goals for {match['team2']}:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("away_"))
async def process_away_goals(callback: CallbackQuery):
    """Handle away team goals selection."""
    await callback.answer()
    
    _, match_id, home_goals, away_goals = callback.data.split("_")
    
    matches = get_matches()
    match = matches.get(match_id)
    
    if match.get("is_knockout", False):
        # For knockout matches, ask for resolution type
        keyboard = get_resolution_type_keyboard(match_id, home_goals, away_goals)
        await callback.message.edit_text(
            f"Selected {home_goals}-{away_goals}.\n"
            f"How will the match be decided?",
            reply_markup=keyboard
        )
    else:
        # For group stage matches, save the prediction
        user_id = str(callback.from_user.id)
        save_prediction(user_id, match_id, int(home_goals), int(away_goals))
        
        await callback.message.edit_text(
            f"Your prediction for {match['team1']} vs {match['team2']} "
            f"is {home_goals}-{away_goals}.\n\n{PREDICTION_SUCCESS}"
        )

@router.callback_query(F.data.startswith("resolution_"))
async def process_resolution_type(callback: CallbackQuery):
    """Handle resolution type selection for knockout matches."""
    await callback.answer()
    
    _, match_id, home_goals, away_goals, resolution_type = callback.data.split("_")
    
    user_id = str(callback.from_user.id)
    matches = get_matches()
    match = matches.get(match_id)
    
    save_prediction(
        user_id, match_id, 
        int(home_goals), int(away_goals), 
        resolution_type
    )
    
    resolution_text = {
        "FT": "Full Time",
        "ET": "Extra Time",
        "PEN": "Penalties"
    }.get(resolution_type, resolution_type)
    
    await callback.message.edit_text(
        f"Your prediction for {match['team1']} vs {match['team2']} "
        f"is {home_goals}-{away_goals} ({resolution_text}).\n\n{PREDICTION_SUCCESS}"
    )

@router.message(Command("mypredictions"))
async def cmd_my_predictions(message: Message):
    """Handle the /mypredictions command."""
    user_id = str(message.from_user.id)
    predictions = get_user_predictions(user_id)
    
    if not predictions:
        await message.answer(NO_PREDICTIONS)
        return
    
    matches = get_matches()
    
    response = "Your predictions:\n\n"
    for match_id, prediction in predictions.items():
        if match_id not in matches:
            continue
        
        match = matches[match_id]
        pred_text = f"{prediction['home_goals']}-{prediction['away_goals']}"
        
        if match.get("is_knockout", False) and "resolution_type" in prediction:
            pred_text += f" ({prediction['resolution_type']})"
        
        response += f"• {match['team1']} vs {match['team2']}: {pred_text}\n"
    
    await message.answer(response)

@router.message(Command("matches"))
async def cmd_matches(message: Message):
    """Handle the /matches command."""
    upcoming_matches = get_upcoming_matches()
    
    if not upcoming_matches:
        await message.answer(NO_UPCOMING_MATCHES)
        return
    
    keyboard = get_match_list_keyboard(upcoming_matches)
    await message.answer(MATCH_LIST_HEADER, reply_markup=keyboard)

@router.callback_query(F.data.startswith("viewmatch_"))
async def process_view_match(callback: CallbackQuery):
    """Handle viewing match details."""
    await callback.answer()
    
    match_id = callback.data.split("_")[1]
    matches = get_matches()
    match = matches.get(match_id)
    
    if not match:
        await callback.message.edit_text("Match not found.")
        return
    
    match_type = "Knockout Stage" if match.get("is_knockout", False) else "Group Stage"
    match_status = "Locked" if match.get("locked", False) else "Open for predictions"
    
    response = (
        f"Match: {match['team1']} vs {match['team2']}\n"
        f"Time: {match['time']}\n"
        f"Type: {match_type}\n"
        f"Status: {match_status}\n"
    )
    
    # Add result if available
    if "result" in match:
        result = match["result"]
        result_text = f"{result['home_goals']}-{result['away_goals']}"
        
        if match.get("is_knockout", False) and "resolution_type" in result:
            result_text += f" ({result['resolution_type']})"
        
        response += f"Result: {result_text}\n"
    
    # Check user prediction
    user_id = str(callback.from_user.id)
    predictions = get_user_predictions(user_id)
    
    if match_id in predictions:
        pred = predictions[match_id]
        pred_text = f"{pred['home_goals']}-{pred['away_goals']}"
        
        if match.get("is_knockout", False) and "resolution_type" in pred:
            pred_text += f" ({pred['resolution_type']})"
        
        response += f"\nYour prediction: {pred_text}"
    
    keyboard = get_match_list_keyboard(get_upcoming_matches())
    await callback.message.edit_text(response, reply_markup=keyboard)

@router.message(Command("leaderboard"))
async def cmd_leaderboard(message: Message):
    """Handle the /leaderboard command."""
    leaderboard = get_leaderboard()
    
    if not leaderboard:
        await message.answer(EMPTY_LEADERBOARD)
        return
    
    response = f"{LEADERBOARD_HEADER}\n\n"
    
    for entry in leaderboard[:10]:  # Show top 10
        name = entry['name']
        if entry['username']:
            name += f" (@{entry['username']})"
        
        response += f"{entry['rank']}. {name}: {entry['score']} pts\n"
    
    await message.answer(response)

@router.message(Command("myrank"))
async def cmd_my_rank(message: Message):
    """Handle the /myrank command."""
    user_id = str(message.from_user.id)
    rank, score = get_user_rank(user_id)
    
    if rank is None:
        await message.answer("You are not yet on the leaderboard.")
        return
    
    await message.answer(RANK_MESSAGE.format(rank, score)) 