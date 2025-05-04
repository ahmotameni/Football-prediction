"""
Entry point for the Club World Cup 2025 Prediction Bot.

This file makes it easy to run the bot directly from the project root.
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the bot module
from club_world_cup_bot.bot import main

if __name__ == "__main__":
    # Run the bot
    import asyncio
    asyncio.run(main()) 