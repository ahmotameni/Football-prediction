"""
Entry point for the Club World Cup 2025 Prediction Bot staged test script.

This file makes it easy to run the staged test script directly from the project root.

Usage:
    python run_staged_test.py [stage_number]
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Run the staged test script
    from club_world_cup_bot.staged_test import main
    main() 