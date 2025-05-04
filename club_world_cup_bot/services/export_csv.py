"""
Service for exporting data to CSV format.
"""
import csv
import os
import io
import glob
from datetime import datetime

from club_world_cup_bot.services.prediction import load_data, PREDICTIONS_FILE, MATCHES_FILE, USERS_FILE

# Directory for exported CSV files
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'exports')
os.makedirs(EXPORTS_DIR, exist_ok=True)

def generate_export_filename():
    """Generate a filename for the export with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"cwc_predictions_{timestamp}.csv"

def export_predictions_csv():
    """Export all predictions and scores to a CSV file."""
    predictions = load_data(PREDICTIONS_FILE)
    matches = load_data(MATCHES_FILE)
    users = load_data(USERS_FILE)
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    header = ["User ID", "Username", "Name", "Score"]
    
    # Add a column for each match
    match_columns = []
    for match_id, match in sorted(matches.items(), key=lambda x: x[0]):
        column_name = f"{match['team1']} vs {match['team2']}"
        match_columns.append((match_id, column_name))
        header.append(column_name)
    
    writer.writerow(header)
    
    # Write data rows
    for user_id, user_data in users.items():
        row = [
            user_id,
            user_data.get('username', ''),
            f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            user_data.get('score', 0)
        ]
        
        # Add prediction for each match
        user_predictions = predictions.get(user_id, {})
        for match_id, _ in match_columns:
            if match_id in user_predictions:
                pred = user_predictions[match_id]
                prediction_text = f"{pred['home_goals']}-{pred['away_goals']}"
                
                # Add resolution type for knockout matches
                if 'resolution_type' in pred:
                    prediction_text += f" ({pred['resolution_type']})"
                
                row.append(prediction_text)
            else:
                row.append("")
        
        writer.writerow(row)
    
    # Get CSV data
    csv_data = output.getvalue()
    output.close()
    
    # Save to file in exports directory
    filename = generate_export_filename()
    filepath = os.path.join(EXPORTS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(csv_data)
    
    # Return CSV data and filename
    return csv_data, filename

def get_exported_files():
    """Get a list of all exported CSV files."""
    files = glob.glob(os.path.join(EXPORTS_DIR, "*.csv"))
    files.sort(key=os.path.getmtime, reverse=True)  # Sort by modification time, newest first
    
    return [os.path.basename(f) for f in files]

def get_file_content(filename):
    """Get the content of an exported CSV file."""
    filepath = os.path.join(EXPORTS_DIR, filename)
    
    if not os.path.exists(filepath) or not filename.endswith('.csv'):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read() 