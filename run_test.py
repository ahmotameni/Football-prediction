"""
Entry point for the Club World Cup 2025 Prediction Bot test script.

This file makes it easy to run the test script directly from the project root.
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Run the test script
    from club_world_cup_bot.test_bot import main
    main() 