#!/usr/bin/env python3
"""
Debug script to test prediction functionality and keyboard generation.
"""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from club_world_cup_bot.firebase_init import initialize_firebase
from club_world_cup_bot.services.prediction import get_matches, get_user_predictions
from club_world_cup_bot.keyboards.prediction_keyboard import get_enhanced_matches_keyboard

def main():
    print("🔥 Initializing Firebase...")
    initialize_firebase()
    print("✅ Firebase initialized")
    
    print("\n📊 Testing data retrieval...")
    
    # Test matches retrieval
    matches = get_matches()
    print(f"📋 Found {len(matches)} matches:")
    for match_id, match in matches.items():
        status = "🔒" if match.get('locked', False) else "⚽"
        result = f" [Result: {match['result']['home_goals']}-{match['result']['away_goals']}]" if 'result' in match else ""
        print(f"  {status} {match_id}: {match['team1']} vs {match['team2']}{result}")
    
    # Test user predictions (use a placeholder user ID for testing)
    test_user_id = "test_user_123"
    print(f"\n🔮 Testing predictions for user {test_user_id}...")
    predictions = get_user_predictions(test_user_id)
    print(f"📝 Found {len(predictions)} predictions:")
    for match_id, pred in predictions.items():
        extra = ""
        if pred.get('resolution_type'):
            extra = f" ({pred['resolution_type']}"
            if pred.get('knockout_winner'):
                extra += f"_{pred['knockout_winner']}"
            extra += ")"
        print(f"  ✅ {match_id}: {pred['home_goals']}-{pred['away_goals']}{extra}")
    
    # Test keyboard generation
    print(f"\n⌨️ Testing keyboard generation...")
    keyboard = get_enhanced_matches_keyboard(matches, predictions)
    print(f"📱 Generated keyboard with {len(keyboard.inline_keyboard)} buttons")
    
    for i, row in enumerate(keyboard.inline_keyboard):
        for j, button in enumerate(row):
            print(f"  🔘 Button {i+1}.{j+1}: {button.text}")
            print(f"     Callback: {button.callback_data}")
    
    print("\n✅ Debug complete!")

if __name__ == "__main__":
    main() 