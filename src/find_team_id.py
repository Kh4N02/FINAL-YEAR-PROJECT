import requests
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cricket_api import CricketAPI

def get_pakistan_squad():
    # Create API instance
    api = CricketAPI()
    
    # Pakistan team ID is 52126 (confirmed from the countries endpoint)
    team_id = 52126
    
    # Get team squad using the API class
    response = api.get_team_players(team_id)
    
    if response.get('status') == 'error':
        print("Error fetching Pakistan squad data")
        print("Response:", response)
        return None
        
    if 'data' in response and 'squad' in response['data']:
        print("\nSuccessfully found Pakistan squad:")
        for player in response['data']['squad']:
            print(f"Player ID: {player['id']}, Name: {player.get('fullname', 'N/A')}")
        return response['data']['squad']
    
    print("Error: Unexpected response format")
    print("Response:", response)
    return None

def main():
    api = CricketAPI()
    print("Testing API connection...")
    test_response = api.test_connection()
    
    if test_response.get('status') == 'error':
        print("API Error:", test_response)
        return
        
    print("\nFetching Pakistan team squad...")
    squad = get_pakistan_squad()
    if squad:
        print(f"\nTotal players found: {len(squad)}")

if __name__ == "__main__":
    main() 