import requests
from pprint import pprint

API_TOKEN = "johiHREyKMRBTqRBF8rwaaCYo4fpg12g3ZUVlS63PUIEKzeXGRtyqfvFBxrj"

def get_match_details(match_id):
    url = f"https://cricket.sportmonks.com/api/v2.0/fixtures/{match_id}"
    params = {
        "api_token": API_TOKEN,
        "include": "bowling,batting"
    }
    response = requests.get(url, params=params)
    return response.json()

def get_recent_matches():
    """Get recent T20I matches for Pakistan"""
    # First get Pakistan's team ID
    team_url = "https://cricket.sportmonks.com/api/v2.0/teams"
    params = {
        "api_token": API_TOKEN,
        "filter[name]": "Pakistan"
    }
    
    team_response = requests.get(team_url, params=params)
    team_id = team_response.json()['data'][0]['id']
    print(f"Pakistan team ID: {team_id}")
    
    # Get recent matches
    fixtures_url = "https://cricket.sportmonks.com/api/v2.0/fixtures"
    params = {
        "api_token": API_TOKEN,
        "filter[type]": "T20I",
        "filter[status]": "Finished",
        "include": "localteam,visitorteam,bowling,batting",
        "sort": "-starting_at",
        "per_page": 5
    }
    
    response = requests.get(fixtures_url, params=params)
    matches = response.json()['data']
    
    # Track Sufiyan's performances
    sufiyan_performances = []
    
    for match in matches:
        print(f"\nMatch: {match['localteam']['name']} vs {match['visitorteam']['name']}")
        print(f"Date: {match['starting_at']}")
        
        # Look for Sufiyan in bowling performances
        bowling = match.get('bowling', [])
        for spell in bowling:
            bowler_name = spell.get('bowler', {}).get('fullname', '')
            if 'Sufiyan' in bowler_name:
                performance = {
                    'date': match['starting_at'],
                    'overs': spell['overs'],
                    'runs': spell['runs'],
                    'wickets': spell['wickets'],
                    'match_id': match['id']
                }
                sufiyan_performances.append(performance)
                print(f"Found Sufiyan's performance:")
                pprint(performance)
    
    print("\nSummary of Sufiyan's performances:")
    total_overs = sum(float(p['overs']) for p in sufiyan_performances)
    total_wickets = sum(p['wickets'] for p in sufiyan_performances)
    total_runs = sum(p['runs'] for p in sufiyan_performances)
    matches_played = len(sufiyan_performances)
    
    print(f"Matches played: {matches_played}")
    print(f"Total overs: {total_overs}")
    print(f"Total wickets: {total_wickets}")
    print(f"Total runs: {total_runs}")
    if total_overs > 0:
        economy = (total_runs * 6) / (int(total_overs) * 6 + (total_overs % 1) * 10)
        print(f"Economy rate: {economy:.2f}")

if __name__ == "__main__":
    print("Debugging API data for Sufiyan's performances...")
    get_recent_matches() 