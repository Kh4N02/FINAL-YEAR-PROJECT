import requests
import json
from datetime import datetime

API_TOKEN = "johiHREyKMRBTqRBF8rwaaCYo4fpg12g3ZUVlS63PUIEKzeXGRtyqfvFBxrj"
BASE_URL = "https://cricket.sportmonks.com/api/v2.0"

class CricketAPI:
    def __init__(self):
        # No headers needed for this API
        self.params = {
            "api_token": API_TOKEN
        }
    
    def get_player_stats(self, player_id):
        url = f"{BASE_URL}/players/{player_id}"
        params = {
            **self.params,
            "include": "career"
        }
        response = requests.get(url, params=params)
        print(f"Player Stats URL: {response.url}")
        return response.json()

    def get_team_players(self, team_id):
        url = f"{BASE_URL}/teams/{team_id}"
        params = {
            **self.params,
            "include": "squad"
        }
        response = requests.get(url, params=params)
        print(f"Team Players URL: {response.url}")
        return response.json()

    def test_connection(self):
        """Test the API connection with a simple endpoint"""
        url = f"{BASE_URL}/countries"
        response = requests.get(url, params=self.params)
        print(f"Test URL: {response.url}")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Find Pakistan in the response to verify we can access it
            pakistan = next((country for country in data['data'] 
                           if country['name'] == 'Pakistan'), None)
            if pakistan:
                print(f"Found Pakistan! ID: {pakistan['id']}")
            return data
        else:
            print(f"Error Response: {response.text}")
            return {"status": "error", "message": response.text} 