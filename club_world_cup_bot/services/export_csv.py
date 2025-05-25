"""
Service for exporting data to CSV format using Firebase Realtime Database.
"""
import csv
import io
from datetime import datetime

from ..firebase_helpers import (
    get_all_users, get_all_matches, get_all_predictions,
    save_export
)

def generate_export_filename():
    """Generate a filename for the export with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"cwc_predictions_{timestamp}.csv"

def export_predictions_csv():
    """Export all predictions and scores to a CSV file and save to Firebase."""
    predictions = get_all_predictions()
    matches = get_all_matches()
    users = get_all_users()
    
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
    
    # Create export record for Firebase
    timestamp = datetime.now()
    export_id = timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"cwc_predictions_{export_id}.csv"
    
    export_data = {
        'filename': filename,
        'csv_data': csv_data,
        'created_at': timestamp.isoformat()
    }
    
    # Save to Firebase
    if save_export(export_id, export_data):
        return True, filename
    else:
        return False, None 