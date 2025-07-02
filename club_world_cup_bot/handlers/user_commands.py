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
    RANK_MESSAGE, ENHANCED_MATCHES_HEADER, NO_MATCH_RESULTS, USER_NOT_WHITELISTED
)
from club_world_cup_bot.keyboards.prediction_keyboard import (
    get_matches_keyboard, get_home_goals_keyboard, 
    get_away_goals_keyboard, get_resolution_type_keyboard, 
    get_match_list_keyboard, get_enhanced_matches_keyboard
)
from club_world_cup_bot.keyboards.persistent_keyboard import (
    get_user_keyboard, get_admin_keyboard
)
from club_world_cup_bot.services.prediction import (
    register_user, get_upcoming_matches, get_matches,
    save_prediction, get_user_predictions, is_admin, is_admin_by_username,
    is_whitelisted, is_whitelisted_by_username
)
from club_world_cup_bot.services.scoring import get_leaderboard, get_user_rank, calculate_score

router = Router()

def check_user_access(user):
    """Check if user has access (is admin or whitelisted)."""
    user_id = str(user.id)
    username = user.username
    
    # Admins always have access
    if is_admin(user_id) or (username and is_admin_by_username(username)):
        return True
    
    # Check if user is whitelisted
    if is_whitelisted(user_id) or (username and is_whitelisted_by_username(username)):
        return True
    
    return False

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

@router.message(F.text == "⚽ Matches")
async def button_matches(message: Message):
    """Handle the Matches button - enhanced version that combines predict and matches."""
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
    await cmd_enhanced_matches(message)

@router.message(F.text == "📋 My Predictions")
async def button_my_predictions(message: Message):
    """Handle the My Predictions button."""
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
    await cmd_my_predictions(message)

@router.message(F.text == "🏆 Leaderboard")
async def button_leaderboard(message: Message):
    """Handle the Leaderboard button."""
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
    await cmd_leaderboard(message)

@router.message(F.text == "🥇 My Rank")
async def button_my_rank(message: Message):
    """Handle the My Rank button."""
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
    await cmd_my_rank(message)

@router.message(Command("predict"))
async def cmd_predict(message: Message):
    """Handle the /predict command - now redirects to enhanced matches."""
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
    await cmd_enhanced_matches(message)

@router.message(Command("enhanced_matches"))
async def cmd_enhanced_matches(message: Message):
    """
    Enhanced matches command that combines match viewing and prediction.
    Shows matches with their status, user predictions if available, and results.
    """
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
        
    user_id = str(message.from_user.id)
    matches = get_matches()
    
    if not matches:
        await message.answer(NO_MATCHES_TO_PREDICT)
        return
    
    # Get user predictions if any
    user_predictions = get_user_predictions(user_id)
    
    # Create enhanced keyboard with predictions and status
    keyboard = get_enhanced_matches_keyboard(matches, user_predictions)
    
    await message.answer(ENHANCED_MATCHES_HEADER, reply_markup=keyboard)

@router.callback_query(F.data.startswith("match_"))
async def process_match_selection(callback: CallbackQuery):
    """Handle match selection for prediction."""
    await callback.answer()
    
    if not check_user_access(callback.from_user):
        await callback.message.edit_text(USER_NOT_WHITELISTED)
        return
    
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
    
    if not check_user_access(callback.from_user):
        await callback.message.edit_text(USER_NOT_WHITELISTED)
        return
    
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
    
    if not check_user_access(callback.from_user):
        await callback.message.edit_text(USER_NOT_WHITELISTED)
        return
    
    _, match_id, home_goals, away_goals = callback.data.split("_")
    
    matches = get_matches()
    match = matches.get(match_id)
    
    if match.get("is_knockout", False):
        home_goals_int = int(home_goals)
        away_goals_int = int(away_goals)
        
        if home_goals_int == away_goals_int:
            # For ties in knockout matches, ask for resolution type and winner
            keyboard = get_resolution_type_keyboard(match_id, home_goals, away_goals)
            await callback.message.edit_text(
                f"Selected {home_goals}-{away_goals} (tie after 90 minutes).\n"
                f"How will the match be decided and who will win?",
                reply_markup=keyboard
            )
        else:
            # For non-ties in knockout matches, set resolution type as FT automatically
            user_id = str(callback.from_user.id)
            # Winner is determined by the score (1 for home, 2 for away)
            winner = "1" if home_goals_int > away_goals_int else "2"
            
            save_prediction(
                user_id, match_id, 
                int(home_goals), int(away_goals), 
                f"FT_{winner}"  # Store as FT_1 or FT_2
            )
            
            # Show confirmation and match list
            user_predictions = get_user_predictions(user_id)
            keyboard = get_enhanced_matches_keyboard(matches, user_predictions)
            
            # Determine winner name
            winner_name = match['team1'] if home_goals_int > away_goals_int else match['team2']
            
            await callback.message.edit_text(
                f"✅ Your prediction for {match['team1']} vs {match['team2']} "
                f"is {home_goals}-{away_goals} ({winner_name} wins in Full Time).\n\n"
                f"All matches:",
                reply_markup=keyboard
            )
    else:
        # For group stage matches, save the prediction
        user_id = str(callback.from_user.id)
        save_prediction(user_id, match_id, int(home_goals), int(away_goals))
        
        # After saving, show the enhanced matches list again
        matches = get_matches()
        user_predictions = get_user_predictions(user_id)
        keyboard = get_enhanced_matches_keyboard(matches, user_predictions)
        
        await callback.message.edit_text(
            f"✅ Your prediction for {match['team1']} vs {match['team2']} "
            f"is {home_goals}-{away_goals}.\n\n"
            f"All matches:",
            reply_markup=keyboard
        )

@router.callback_query(F.data.startswith("resolution_"))
async def process_resolution_type(callback: CallbackQuery):
    """Handle resolution type selection for knockout matches."""
    await callback.answer()
    
    if not check_user_access(callback.from_user):
        await callback.message.edit_text(USER_NOT_WHITELISTED)
        return
    
    # Split callback data safely
    parts = callback.data.split("_")
    # First 4 parts: resolution, match_id, home_goals, away_goals
    # Everything else will be part of resolution_data
    if len(parts) < 5:
        await callback.message.edit_text("Invalid callback data")
        return
    
    match_id = parts[1]
    home_goals = parts[2]
    away_goals = parts[3]
    # Join remaining parts back together with underscores for full resolution_data
    resolution_data = "_".join(parts[4:])
    
    user_id = str(callback.from_user.id)
    matches = get_matches()
    match = matches.get(match_id)
    
    # Parse resolution type and winner from resolution_data
    if "_" in resolution_data:
        resolution_type, knockout_winner = resolution_data.split("_", 1)  # Split only on first underscore
    else:
        resolution_type = resolution_data
        knockout_winner = None
    
    # Save the prediction
    prediction_data = {
        'home_goals': int(home_goals),
        'away_goals': int(away_goals),
        'resolution_type': resolution_type
    }
    
    # Add knockout winner if available
    if knockout_winner:
        prediction_data['knockout_winner'] = knockout_winner
    
    # Save prediction with all data - construct the resolution string
    if knockout_winner:
        resolution_string = f"{resolution_type}_{knockout_winner}"
    else:
        resolution_string = resolution_type
    
    save_prediction(user_id, match_id, int(home_goals), int(away_goals), resolution_string)
    
    # Format resolution text for display
    resolution_text = resolution_type
    winner_name = None
    
    if knockout_winner == "1":
        winner_name = match['team1']
    elif knockout_winner == "2":
        winner_name = match['team2']
    
    if resolution_type == "ET" and winner_name:
        resolution_text = f"{winner_name} wins in Extra Time"
    elif resolution_type == "PEN" and winner_name:
        resolution_text = f"{winner_name} wins in Penalties"
    elif resolution_type == "FT" and winner_name:
        resolution_text = f"{winner_name} wins in Full Time"
    else:
        resolution_text = {
            "FT": "Full Time",
            "ET": "Extra Time",
            "PEN": "Penalties"
        }.get(resolution_type, resolution_type)
    
    # After saving, show the enhanced matches list again
    user_predictions = get_user_predictions(user_id)
    keyboard = get_enhanced_matches_keyboard(matches, user_predictions)
    
    await callback.message.edit_text(
        f"✅ Your prediction for {match['team1']} vs {match['team2']} "
        f"is {home_goals}-{away_goals} ({resolution_text}).\n\n"
        f"All matches:",
        reply_markup=keyboard
    )

@router.message(Command("mypredictions"))
async def cmd_my_predictions(message: Message):
    """Handle the /mypredictions command - now using the enhanced match display."""
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
        
    user_id = str(message.from_user.id)
    predictions = get_user_predictions(user_id)
    
    if not predictions:
        await message.answer(NO_PREDICTIONS)
        return
    
    matches = get_matches()
    # Filter to only show matches that user has predicted
    predicted_matches = {match_id: match for match_id, match in matches.items() 
                        if match_id in predictions}
    
    keyboard = get_enhanced_matches_keyboard(predicted_matches, predictions)
    await message.answer("📋 Your Predictions:", reply_markup=keyboard)

@router.message(Command("matches"))
async def cmd_matches(message: Message):
    """Handle the /matches command - redirects to enhanced matches."""
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
    await cmd_enhanced_matches(message)

@router.callback_query(F.data.startswith("viewmatch_"))
async def process_view_match(callback: CallbackQuery):
    """Handle viewing match details."""
    await callback.answer()
    
    if not check_user_access(callback.from_user):
        await callback.message.edit_text(USER_NOT_WHITELISTED)
        return
    
    match_id = callback.data.split("_")[1]
    matches = get_matches()
    match = matches.get(match_id)
    
    if not match:
        await callback.message.edit_text("Match not found.")
        return
    
    match_type = "Knockout Stage" if match.get("is_knockout", False) else "Group Stage"
    match_status = "Locked 🔒" if match.get("locked", False) else "Open for predictions ⚽"
    
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
        
        # Format result text for knockout matches
        if match.get("is_knockout", False) and "resolution_type" in result:
            resolution_type = result["resolution_type"]
            
            # For ties with winner info (ET/PEN)
            if int(result['home_goals']) == int(result['away_goals']):
                knockout_winner = result.get("knockout_winner")
                if knockout_winner:
                    winner_name = match['team1'] if knockout_winner == "1" else match['team2']
                    resolution_full = {
                        "ET": f"{winner_name} wins in Extra Time",
                        "PEN": f"{winner_name} wins in Penalties"
                    }.get(resolution_type, resolution_type)
                    result_text += f" ({resolution_full})"
            else:
                # For non-ties
                result_text += " (Full Time)"
        
        response += f"Result: {result_text}\n"
    
    # Check user prediction
    user_id = str(callback.from_user.id)
    predictions = get_user_predictions(user_id)
    
    if match_id in predictions:
        pred = predictions[match_id]
        pred_text = f"{pred['home_goals']}-{pred['away_goals']}"
        
        # Format prediction text for knockout matches
        if match.get("is_knockout", False) and "resolution_type" in pred:
            resolution_type = pred["resolution_type"]
            
            # For ties with winner info (ET/PEN)
            if int(pred['home_goals']) == int(pred['away_goals']):
                knockout_winner = pred.get("knockout_winner")
                if knockout_winner:
                    winner_name = match['team1'] if knockout_winner == "1" else match['team2']
                    resolution_full = {
                        "ET": f"{winner_name} wins in Extra Time",
                        "PEN": f"{winner_name} wins in Penalties"
                    }.get(resolution_type, resolution_type)
                    pred_text += f" ({resolution_full})"
            else:
                # For non-ties
                pred_text += " (Full Time)"
        
        response += f"\n🔮 Your prediction: {pred_text}"
    
    # Get back to matches list
    user_predictions = get_user_predictions(user_id)
    keyboard = get_enhanced_matches_keyboard(matches, user_predictions)
    
    await callback.message.edit_text(response, reply_markup=keyboard)

@router.callback_query(F.data.startswith("viewresult_"))
async def process_view_result(callback: CallbackQuery):
    """Handle viewing match results."""
    await callback.answer()
    
    if not check_user_access(callback.from_user):
        await callback.message.edit_text(USER_NOT_WHITELISTED)
        return
    
    match_id = callback.data.split("_")[1]
    matches = get_matches()
    match = matches.get(match_id)
    user_id = str(callback.from_user.id)
    predictions = get_user_predictions(user_id)
    
    if not match or "result" not in match:
        await callback.message.edit_text(NO_MATCH_RESULTS)
        return
    
    match_type = "Knockout Stage" if match.get("is_knockout", False) else "Group Stage"
    result = match["result"]
    result_text = f"{result['home_goals']}-{result['away_goals']}"
    
    # Format result text for knockout matches
    if match.get("is_knockout", False) and "resolution_type" in result:
        resolution_type = result["resolution_type"]
        
        # For ties with winner info (ET/PEN)
        if int(result['home_goals']) == int(result['away_goals']):
            knockout_winner = result.get("knockout_winner")
            if knockout_winner:
                winner_name = match['team1'] if knockout_winner == "1" else match['team2']
                resolution_full = {
                    "ET": f"{winner_name} wins in Extra Time",
                    "PEN": f"{winner_name} wins in Penalties"
                }.get(resolution_type, resolution_type)
                result_text += f" ({resolution_full})"
        else:
            # For non-ties
            result_text += " (Full Time)"
    
    response = (
        f"✅ Match Result:\n"
        f"{match['team1']} vs {match['team2']}\n"
        f"Time: {match['time']}\n"
        f"Type: {match_type}\n"
        f"Final Score: {result_text}\n\n"
    )
    
    # Show user prediction and points if available
    if match_id in predictions:
        pred = predictions[match_id]
        pred_text = f"{pred['home_goals']}-{pred['away_goals']}"
        
        # Format prediction text for knockout matches
        if match.get("is_knockout", False) and "resolution_type" in pred:
            resolution_type = pred["resolution_type"]
            
            # For ties with winner info (ET/PEN)
            if int(pred['home_goals']) == int(pred['away_goals']):
                knockout_winner = pred.get("knockout_winner")
                if knockout_winner:
                    winner_name = match['team1'] if knockout_winner == "1" else match['team2']
                    resolution_full = {
                        "ET": f"{winner_name} wins in Extra Time",
                        "PEN": f"{winner_name} wins in Penalties"
                    }.get(resolution_type, resolution_type)
                    pred_text += f" ({resolution_full})"
            else:
                # For non-ties
                pred_text += " (Full Time)"
        
        # Calculate points earned
        points = calculate_score(pred, result, match)
        
        response += (
            f"🔮 Your prediction: {pred_text}\n"
            f"🏆 Points earned: {points}\n"
        )
    
    # Get back to matches list
    keyboard = get_enhanced_matches_keyboard(matches, predictions)
    await callback.message.edit_text(response, reply_markup=keyboard)

@router.message(Command("leaderboard"))
async def cmd_leaderboard(message: Message):
    """Handle the /leaderboard command."""
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
        
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
    if not check_user_access(message.from_user):
        await message.answer(USER_NOT_WHITELISTED)
        return
        
    user_id = str(message.from_user.id)
    rank, score = get_user_rank(user_id)
    
    if rank is None:
        await message.answer("You are not yet on the leaderboard.")
        return
    
    await message.answer(RANK_MESSAGE.format(rank, score)) 