"""
Firebase initialization module for the Club World Cup Bot.

This module sets up the Firebase Admin SDK connection using service account credentials
and provides a database reference for other modules to use.
"""
import json
import base64
import os
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase only once
_firebase_initialized = False
_database_ref = None

def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    global _firebase_initialized, _database_ref
    
    if _firebase_initialized:
        return _database_ref
    
    try:
        # Check if we're on Heroku (production) or local development
        firebase_key_env = os.getenv("FIREBASE_KEY")
        
        if firebase_key_env:
            # Production: Use base64 encoded service account key from environment
            firebase_key = base64.b64decode(firebase_key_env).decode()
            cred = credentials.Certificate(json.loads(firebase_key))
        else:
            # Development: Use local service account key file
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            service_account_path = os.path.join(script_dir, 'serviceAccountKey.json')
            
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
            else:
                raise FileNotFoundError("Firebase service account key not found. Please set FIREBASE_KEY environment variable or place serviceAccountKey.json in the project root.")
        
        # Initialize the app with database URL
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://fff-prediction-default-rtdb.europe-west1.firebasedatabase.app'
        })
        
        # Get database reference
        _database_ref = db.reference('/')
        _firebase_initialized = True
        
        print("Firebase initialized successfully")
        return _database_ref
        
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        raise e

def get_database():
    """Get the Firebase database reference."""
    if not _firebase_initialized:
        return initialize_firebase()
    return _database_ref

# Initialize Firebase when module is imported
database = initialize_firebase() 