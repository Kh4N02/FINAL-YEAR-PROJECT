import requests

API_TOKEN = "johiHREyKMRBTqRBF8rwaaCYo4fpg12g3ZUVlS63PUIEKzeXGRtyqfvFBxrj"

def get_pakistan_data():
    """Get Pakistan's cricket data including teams and players"""
    
    # First get Pakistan's country data
    url = "https://cricket.sportmonks.com/api/v2.0/countries"
    params = {
        "api_token": API_TOKEN,
        "include": "teams"  # Include teams data
    }
    
    print("Fetching Pakistan's data...")
    try:
        response = requests.get(url, params=params)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Find Pakistan in the response
            pakistan = next((country for country in data['data'] 
                           if country['name'] == 'Pakistan'), None)
            
            if pakistan:
                print("\nPakistan Data:")
                print(f"ID: {pakistan['id']}")
                print(f"Name: {pakistan['name']}")
                print(f"Continent ID: {pakistan['continent_id']}")
                
                # Get Pakistan's teams
                teams_url = f"https://cricket.sportmonks.com/api/v2.0/teams/country/{pakistan['id']}"
                teams_response = requests.get(teams_url, params={"api_token": API_TOKEN})
                
                if teams_response.status_code == 200:
                    teams_data = teams_response.json()
                    print("\nPakistan Teams:")
                    for team in teams_data.get('data', []):
                        print(f"Team ID: {team['id']}")
                        print(f"Team Name: {team['name']}")
                        print(f"National Team: {'Yes' if team.get('national_team') else 'No'}")
                        print("---")
                    
                    # Get the national team ID for future use
                    national_team = next((team for team in teams_data.get('data', []) 
                                       if team.get('national_team')), None)
                    if national_team:
                        print(f"\nPakistan National Team ID: {national_team['id']}")
                        return national_team['id']
                else:
                    print("Error fetching teams data:", teams_response.text)
            else:
                print("Pakistan not found in countries data")
        else:
            print("Error in response:", response.text)
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
    
    return None

def get_team_players(team_id):
    """Get players for a specific team"""
    
    url = f"https://cricket.sportmonks.com/api/v2.0/teams/{team_id}"
    params = {
        "api_token": API_TOKEN,
        "include": "squad"  # Include squad/players data
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            squad = data.get('data', {}).get('squad', [])
            
            print(f"\nTeam Squad ({len(squad)} players):")
            for player in squad:
                print(f"Player ID: {player['id']}")
                print(f"Name: {player.get('fullname', 'N/A')}")
                print(f"Position: {player.get('position', {}).get('name', 'N/A')}")
                print("---")
            
            return squad
        else:
            print("Error fetching squad data:", response.text)
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
    
    return None

if __name__ == "__main__":
    print("Getting Pakistan cricket data...")
    team_id = get_pakistan_data()
    
    if team_id:
        print("\nFetching team players...")
        players = get_team_players(team_id)
        
        if players:
            print(f"\nTotal players found: {len(players)}") 