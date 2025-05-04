"""
Club World Cup 2025 Prediction Bot

This bot allows users to predict match results for the 2025 FIFA Club World Cup.
"""
import os
import logging
import asyncio
from datetime import datetime, timedelta

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv("credentials.env")  # Load from credentials.env file
load_dotenv("club_world_cup_bot/credentials.env")

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from club_world_cup_bot.handlers import user_commands, admin_commands
from club_world_cup_bot.services.prediction import lock_expired_matches, set_admin_by_username, get_matches
from club_world_cup_bot.services.scoring import update_leaderboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get the bot token from environment variable
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set")

# For development/testing, add your Telegram username to be set as admin
ADMIN_USERNAME = os.environ.get("ADMIN_USER_ID")  # The env var is still called ADMIN_USER_ID but contains username

async def on_startup(bot: Bot):
    """Actions to perform when the bot starts."""
    logging.info("Bot is starting...")
    
    # Set admin user if specified
    if ADMIN_USERNAME:
        set_admin_by_username(ADMIN_USERNAME)
        logging.info(f"Set user @{ADMIN_USERNAME} as admin")
    
    # Lock any expired matches
    locked = lock_expired_matches()
    if locked:
        logging.info("Locked expired matches")
    
    # Update leaderboard at startup
    update_leaderboard()
    logging.info("Updated leaderboard at startup")

async def lock_matches_job():
    """Job to lock matches that have started."""
    locked = lock_expired_matches()
    if locked:
        logging.info("Locked matches in scheduled job")
        update_leaderboard()

async def send_match_reminders(bot: Bot):
    """Send reminders for upcoming matches."""
    matches = get_matches()
    now = datetime.now()
    
    for match_id, match in matches.items():
        if match.get("locked", False) or "reminder_sent" in match:
            continue
        
        try:
            match_time = datetime.strptime(match["time"], "%Y-%m-%d %H:%M")
            time_diff = match_time - now
            
            # If match is starting in less than 24 hours but more than 23
            if timedelta(hours=23) < time_diff <= timedelta(hours=24):
                # Logic for sending reminders would go here
                # This would require tracking all users
                # For simplicity, we're not implementing this fully
                logging.info(f"Would send reminder for match {match_id}: {match['team1']} vs {match['team2']}")
                
                # Mark as reminded
                match["reminder_sent"] = True
        except Exception as e:
            logging.error(f"Error sending reminder for match {match_id}: {e}")

async def main():
    """Main function to start the bot."""
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register handlers
    dp.include_router(user_commands.router)
    dp.include_router(admin_commands.router)
    
    # Initialize scheduler
    scheduler = AsyncIOScheduler()
    
    # Schedule jobs
    scheduler.add_job(lock_matches_job, 'interval', minutes=5)
    scheduler.add_job(
        send_match_reminders, 'interval', 
        hours=1, args=[bot]
    )
    
    # Start the scheduler
    scheduler.start()
    
    # Register startup callback
    dp.startup.register(on_startup)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 