import requests
import time
import json
from datetime import datetime
import os

API_TOKEN = "johiHREyKMRBTqRBF8rwaaCYo4fpg12g3ZUVlS63PUIEKzeXGRtyqfvFBxrj"

def make_request(url, params):
    """Make API request with rate limit handling"""
    try:
        print(f"Making request to: {url}")
        response = requests.get(url, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            
        return response
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def get_recent_t20i_performances(team_id=None):
    """Get recent T20I performances for a team's players"""
    if team_id is None:
        team_id = 1  # Default to Pakistan
    
    # Get team data
    team_url = "https://cricket.sportmonks.com/api/v2.0/teams"
    team_params = {
        "api_token": API_TOKEN,
        "filter[id]": team_id
    }
    
    print(f"Getting team data for ID: {team_id}...")
    team_response = make_request(team_url, team_params)
    if not team_response or team_response.status_code != 200:
        return None
    
    team_data = team_response.json().get('data', [])[0]
    team_name = team_data.get('name')
    print(f"Found team: {team_name}")
    
    # Get recent T20I fixtures where Pakistan was either local or visitor team
    fixtures_url = "https://cricket.sportmonks.com/api/v2.0/fixtures"
    fixtures_params = {
        "api_token": API_TOKEN,
        "filter[type]": "T20I",
        "filter[status]": "Finished",
        "$or[localteam_id]": team_id,
        "$or[visitorteam_id]": team_id,
        "include": "localteam,visitorteam,batting.batsman,bowling.bowler",
        "sort": "-starting_at",
        "per_page": 5  # Last 5 matches
    }
    
    print("\nFetching recent T20I matches...")
    fixtures_response = make_request(fixtures_url, fixtures_params)
    if not fixtures_response or fixtures_response.status_code != 200:
        # Try alternative approach using league_id for T20Is
        fixtures_params = {
            "api_token": API_TOKEN,
            "filter[league_id]": 3,  # T20I league ID
            "filter[status]": "Finished",
            "include": "localteam,visitorteam,batting.batsman,bowling.bowler",
            "sort": "-starting_at",
            "per_page": 20  # Get more matches to filter Pakistan's matches
        }
        
        print("\nTrying alternative approach...")
        fixtures_response = make_request(fixtures_url, fixtures_params)
        if not fixtures_response or fixtures_response.status_code != 200:
            return None
    
    matches = fixtures_response.json().get('data', [])
    
    # Filter matches where Pakistan played
    pakistan_matches = []
    for match in matches:
        local_team = match.get('localteam', {}).get('id')
        visitor_team = match.get('visitorteam', {}).get('id')
        
        if team_id in [local_team, visitor_team]:
            pakistan_matches.append(match)
            if len(pakistan_matches) >= 5:  # Only get last 5 matches
                break
    
    print(f"\nFound {len(pakistan_matches)} Pakistan T20I matches")
    
    # Collect player performances
    player_performances = {}
    
    for match in pakistan_matches:
        match_date = match.get('starting_at')
        print(f"\nProcessing match from {match_date}")
        local_team = match.get('localteam', {})
        visitor_team = match.get('visitorteam', {})
        print(f"{local_team.get('name')} vs {visitor_team.get('name')}")
        
        # Determine which team is Pakistan
        is_pakistan_local = local_team.get('name') == 'Pakistan'
        pakistan_team_id = local_team.get('id') if is_pakistan_local else visitor_team.get('id')
        
        # Process batting performances - only Pakistani players
        batting = match.get('batting', [])
        for innings in batting:
            if innings.get('team_id') == pakistan_team_id:  # Only Pakistani team players
                batsman = innings.get('batsman', {})
                player_id = batsman.get('id')
                
                if player_id not in player_performances:
                    player_performances[player_id] = {
                        'id': player_id,
                        'name': batsman.get('fullname'),
                        'matches': 0,
                        'batting': {
                            'innings': 0,
                            'runs': 0,
                            'balls': 0,
                            'fours': 0,
                            'sixes': 0,
                            'highest': 0
                        },
                        'bowling': {
                            'innings': 0,
                            'overs': 0,
                            'wickets': 0,
                            'runs': 0,
                            'best': '0/0'
                        }
                    }
                
                perf = player_performances[player_id]
                perf['matches'] += 1
                perf['batting']['innings'] += 1
                perf['batting']['runs'] += innings.get('score', 0)
                perf['batting']['balls'] += innings.get('ball', 0)
                perf['batting']['fours'] += innings.get('four_x', 0)
                perf['batting']['sixes'] += innings.get('six_x', 0)
                
                score = innings.get('score', 0)
                if score > perf['batting']['highest']:
                    perf['batting']['highest'] = score
        
        # Process bowling performances - only Pakistani players
        bowling = match.get('bowling', [])
        for spell in bowling:
            if spell.get('team_id') == pakistan_team_id:  # Only Pakistani team players
                bowler = spell.get('bowler', {})
                player_id = bowler.get('id')
                
                if player_id not in player_performances:
                    continue  # Skip if player not already in batting
                    
                perf = player_performances[player_id]
                perf['bowling']['innings'] += 1
                perf['bowling']['overs'] += spell.get('overs', 0)
                perf['bowling']['wickets'] += spell.get('wickets', 0)
                perf['bowling']['runs'] += spell.get('runs', 0)
                
                wickets = spell.get('wickets', 0)
                runs = spell.get('runs', 0)
                current = f"{wickets}/{runs}"
                if wickets > int(perf['bowling']['best'].split('/')[0]):
                    perf['bowling']['best'] = current
    
    return player_performances

def save_performances(performances, filename=None):
    """Save player performances to a JSON file"""
    if filename is None:
        filename = f"pakistan_t20i_performances_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    filepath = os.path.join(data_dir, filename)
    
    data = {
        'team': 'Pakistan',
        'format': 'T20I',
        'collection_date': datetime.now().isoformat(),
        'players': list(performances.values())
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nData saved to {filepath}")

def calculate_player_rating(player):
    """Calculate a player's rating based on recent performances"""
    batting_stats = player['batting']
    bowling_stats = player['bowling']
    
    # Identify known players and their roles
    KNOWN_PLAYERS = {
        'Mohammad Rizwan': 'Wicketkeeper',
        'Sarfaraz Ahmed': 'Wicketkeeper',
        'Babar Azam': 'Batsman',
        'Fakhar Zaman': 'Batsman',
        'Shaheen Afridi': 'Bowler',
        'Haris Rauf': 'Bowler',
        'Shadab Khan': 'All-rounder',
        'Iftikhar Ahmed': 'All-rounder',
        'Mohammad Nawaz': 'All-rounder',
        'Naseem Shah': 'Bowler',
        'Mohammad Wasim Jr': 'Bowler'
    }
    
    # Calculate ratings
    batting_rating = 0
    if batting_stats['innings'] > 0:
        avg = batting_stats['runs'] / batting_stats['innings']
        sr = (batting_stats['runs'] / batting_stats['balls'] * 100) if batting_stats['balls'] > 0 else 0
        boundary_percent = ((batting_stats['fours'] + batting_stats['sixes']) / batting_stats['balls'] * 100) if batting_stats['balls'] > 0 else 0
        
        batting_rating = min(100, (
            avg * 0.4 +
            sr * 0.4 +
            boundary_percent * 0.2
        ))
    
    bowling_rating = 0
    if bowling_stats['innings'] > 0:
        avg = bowling_stats['runs'] / bowling_stats['wickets'] if bowling_stats['wickets'] > 0 else 100
        economy = bowling_stats['runs'] / bowling_stats['overs'] if bowling_stats['overs'] > 0 else 12
        wickets_per_match = bowling_stats['wickets'] / bowling_stats['innings']
        
        bowling_rating = min(100, (
            (30 - avg) * 2 +
            (12 - economy) * 5 +
            wickets_per_match * 20
        ))
    
    # Determine role based on known players first, then stats
    name = player['name']
    if name in KNOWN_PLAYERS:
        role = KNOWN_PLAYERS[name]
    else:
        # Determine role based on stats
        if bowling_stats['innings'] > 0 and bowling_stats['wickets'] > 0:
            if batting_stats['innings'] > 0 and batting_stats['runs'] / batting_stats['innings'] > 15:
                role = "All-rounder"
            else:
                role = "Bowler"
        else:
            role = "Batsman"
    
    # Calculate overall rating based on role
    if role == "Wicketkeeper":
        overall_rating = batting_rating * 0.9 + bowling_rating * 0.1
    elif role == "Batsman":
        overall_rating = batting_rating
    elif role == "Bowler":
        overall_rating = bowling_rating
    else:  # All-rounder
        overall_rating = (batting_rating + bowling_rating) / 2
    
    return {
        'name': name,
        'role': role,
        'batting_rating': batting_rating,
        'bowling_rating': bowling_rating,
        'overall_rating': overall_rating
    }

def predict_best_xi(performances):
    """Predict the best XI based on recent performances"""
    rated_players = [calculate_player_rating(player) for player in performances.values()]
    
    # Separate players by role
    wicketkeepers = sorted(
        [p for p in rated_players if p['role'] == "Wicketkeeper"],
        key=lambda x: x['overall_rating'],
        reverse=True
    )
    batsmen = sorted(
        [p for p in rated_players if p['role'] == "Batsman"],
        key=lambda x: x['overall_rating'],
        reverse=True
    )
    bowlers = sorted(
        [p for p in rated_players if p['role'] == "Bowler"],
        key=lambda x: x['overall_rating'],
        reverse=True
    )
    allrounders = sorted(
        [p for p in rated_players if p['role'] == "All-rounder"],
        key=lambda x: x['overall_rating'],
        reverse=True
    )
    
    best_xi = []
    
    # 1. Select wicketkeeper (mandatory)
    if wicketkeepers:
        best_xi.append(('wicketkeeper', wicketkeepers[0]))
    elif batsmen:  # If no specialist keeper, use a batsman
        best_xi.append(('wicketkeeper', batsmen[0]))
        batsmen = batsmen[1:]
    
    # 2. Select top order batsmen (3-4)
    for i in range(min(4, len(batsmen))):
        best_xi.append(('batsman', batsmen[i]))
    
    # 3. Select all-rounders (2-3)
    for i in range(min(3, len(allrounders))):
        best_xi.append(('allrounder', allrounders[i]))
    
    # 4. Select bowlers (remaining spots, minimum 4)
    remaining_spots = 11 - len(best_xi)
    for i in range(min(remaining_spots, len(bowlers))):
        best_xi.append(('bowler', bowlers[i]))
    
    # If we still need players, add more batsmen or all-rounders
    while len(best_xi) < 11:
        if len(batsmen) > 4:
            best_xi.append(('batsman', batsmen[4]))
            batsmen = batsmen[5:]
        elif len(allrounders) > 3:
            best_xi.append(('allrounder', allrounders[3]))
            allrounders = allrounders[4:]
        else:
            break
    
    # Organize for display
    return {
        'wicketkeeper': [p[1] for p in best_xi if p[0] == 'wicketkeeper'],
        'batsmen': [p[1] for p in best_xi if p[0] == 'batsman'],
        'allrounders': [p[1] for p in best_xi if p[0] == 'allrounder'],
        'bowlers': [p[1] for p in best_xi if p[0] == 'bowler'],
        'total_rating': sum(p[1]['overall_rating'] for p in best_xi) / len(best_xi) if best_xi else 0
    }

if __name__ == "__main__":
    print("Starting Pakistan T20I performance analysis...")
    performances = get_recent_t20i_performances()
    
    if performances:
        print(f"\nCollected data for {len(performances)} players")
        save_performances(performances)
        
        # Predict best XI
        best_xi = predict_best_xi(performances)
        
        print("\nPredicted Best XI:")
        print("\nWicketkeeper:")
        for player in best_xi['wicketkeeper']:
            print(f"{player['name']} - Rating: {player['batting_rating']:.1f}")
        
        print("\nBatsmen:")
        for player in best_xi['batsmen']:
            print(f"{player['name']} - Rating: {player['batting_rating']:.1f}")
        
        print("\nAll-rounders:")
        for player in best_xi['allrounders']:
            print(f"{player['name']} - Batting: {player['batting_rating']:.1f}, Bowling: {player['bowling_rating']:.1f}")
        
        print("\nBowlers:")
        for player in best_xi['bowlers']:
            print(f"{player['name']} - Rating: {player['bowling_rating']:.1f}")
        
        print(f"\nTeam Rating: {best_xi['total_rating']:.1f}")
        
        # Verify team composition
        total_players = (
            len(best_xi['wicketkeeper']) +
            len(best_xi['batsmen']) +
            len(best_xi['allrounders']) +
            len(best_xi['bowlers'])
        )
        print(f"\nTotal players selected: {total_players}")
    else:
        print("Failed to collect performance data") 