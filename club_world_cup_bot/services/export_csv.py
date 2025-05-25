"""
Service for exporting data to CSV format using Firebase Realtime Database.
"""
import csv
import io
from datetime import datetime

from ..firebase_helpers import (
    get_all_users, get_all_matches, get_all_predictions,
    save_export, get_all_exports, get_export, delete_export
)

def generate_export_filename():
    """Generate a filename for the export with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"cwc_predictions_{timestamp}.csv"

def export_predictions_csv_to_firebase():
    """Export all predictions and scores to a CSV and save to Firebase."""
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
        'id': export_id,
        'filename': filename,
        'csv_data': csv_data,
        'created_at': timestamp.isoformat(),
        'total_users': len(users),
        'total_matches': len(matches),
        'total_predictions': sum(len(user_preds) for user_preds in predictions.values())
    }
    
    # Save to Firebase
    if save_export(export_id, export_data):
        return export_id, export_data
    else:
        return None, None

def export_predictions_csv():
    """Export all predictions and scores to a CSV file (legacy function for compatibility)."""
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
    
    # Return CSV data and filename
    filename = generate_export_filename()
    return csv_data, filename

def get_exports_list():
    """Get a formatted list of all exports."""
    exports = get_all_exports()
    
    export_list = []
    for export_id, export_data in exports.items():
        export_info = {
            'id': export_id,
            'filename': export_data.get('filename', f'export_{export_id}.csv'),
            'created_at': export_data.get('created_at', ''),
            'total_users': export_data.get('total_users', 0),
            'total_matches': export_data.get('total_matches', 0),
            'total_predictions': export_data.get('total_predictions', 0)
        }
        export_list.append(export_info)
    
    # Sort by creation date (newest first)
    export_list.sort(key=lambda x: x['created_at'], reverse=True)
    return export_list

def get_export_csv_data(export_id):
    """Get CSV data for a specific export."""
    export_data = get_export(export_id)
    if export_data and 'csv_data' in export_data:
        return export_data['csv_data'], export_data.get('filename', f'export_{export_id}.csv')
    return None, None 