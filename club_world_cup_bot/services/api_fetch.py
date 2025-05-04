"""
Service for fetching match data from the API-Football API.
"""
import os
import requests
from datetime import datetime

class APIFootballClient:
    """Client for interacting with the API-Football API."""
    
    BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
    
    def __init__(self, api_key=None):
        """Initialize the API client."""
        self.api_key = api_key or os.environ.get("API_FOOTBALL_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set API_FOOTBALL_KEY environment variable.")
        
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
    
    def fetch_matches(self, league_id, season):
        """Fetch matches for a specific league and season."""
        url = f"{self.BASE_URL}/fixtures"
        
        params = {
            "league": league_id,
            "season": season
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data["response"]
        
        return None
    
    def fetch_match_result(self, fixture_id):
        """Fetch result for a specific match."""
        url = f"{self.BASE_URL}/fixtures"
        
        params = {"id": fixture_id}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data["results"] > 0:
                return data["response"][0]
        
        return None
    
    def search_teams(self, name):
        """Search for teams by name."""
        url = f"{self.BASE_URL}/teams"
        
        params = {"search": name}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data["response"]
        
        return None

def format_match_data(api_data):
    """Format API response into match data format for our application."""
    try:
        # Extract teams
        home_team = api_data["teams"]["home"]["name"]
        away_team = api_data["teams"]["away"]["name"]
        
        # Extract fixture date
        fixture_date = api_data["fixture"]["date"]
        fixture_datetime = datetime.fromisoformat(fixture_date.replace("Z", "+00:00"))
        formatted_time = fixture_datetime.strftime("%Y-%m-%d %H:%M")
        
        # Determine if knockout stage
        league_round = api_data["league"]["round"]
        is_knockout = "Group" not in league_round
        
        # Create match data
        match_data = {
            "team1": home_team,
            "team2": away_team,
            "time": formatted_time,
            "is_knockout": is_knockout,
            "api_fixture_id": api_data["fixture"]["id"],
            "locked": False
        }
        
        # Check if match has results
        if api_data["fixture"]["status"]["short"] in ["FT", "AET", "PEN"]:
            # Extract goals
            home_goals = api_data["goals"]["home"]
            away_goals = api_data["goals"]["away"]
            
            # Extract resolution type
            status = api_data["fixture"]["status"]["short"]
            resolution_type = "FT"
            if status == "AET":
                resolution_type = "ET"
            elif status == "PEN":
                resolution_type = "PEN"
            
            # Add result
            match_data["result"] = {
                "home_goals": home_goals,
                "away_goals": away_goals
            }
            
            if is_knockout:
                match_data["result"]["resolution_type"] = resolution_type
            
            match_data["locked"] = True
        
        return match_data
    
    except (KeyError, ValueError) as e:
        print(f"Error formatting match data: {e}")
        return None

def fetch_match_by_teams(api_client, team1, team2, date=None):
    """Find a match between two teams, optionally on a specific date."""
    # This is a simplified implementation. In practice, you'd need to:
    # 1. Search for the teams to get their IDs
    # 2. Use the team IDs to search for fixtures between them
    # 3. Filter by date if provided
    
    # For demonstration, we'll just return None since this would require 
    # multiple API calls and complex logic
    return None 