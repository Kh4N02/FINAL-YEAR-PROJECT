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

def get_team_name(team_id):
    """Get team name from team ID"""
    # First get all teams
    team_url = "https://cricket.sportmonks.com/api/v2.0/teams"
    team_params = {
        "api_token": API_TOKEN,
        "per_page": 100  # Get more teams to ensure we find the one we want
    }
    
    response = make_request(team_url, team_params)
    if response and response.status_code == 200:
        data = response.json()
        if data.get('data'):
            # Find the team with matching ID
            for team in data['data']:
                if team.get('id') == team_id:
                    return team.get('name')
    return None

def get_team_players(team_id):
    """Get all players for a team"""
    # First get team details
    team_name = get_team_name(team_id)
    if not team_name:
        print(f"Could not find team with ID {team_id}")
        return None
        
    # Then get team squad
    team_url = f"https://cricket.sportmonks.com/api/v2.0/teams/{team_id}"
    team_params = {
        "api_token": API_TOKEN,
        "include": "squad"
    }
    
    response = make_request(team_url, team_params)
    if not response or response.status_code != 200:
        return None
        
    data = response.json()
    if not data.get('data'):
        return None
        
    team_data = data['data']
    squad = team_data.get('squad', {}).get('data', [])
    
    # If squad is a list, use it directly
    if isinstance(squad, list):
        players_list = squad
    else:
        # If squad is a dict, try to get the data field
        players_list = squad.get('data', [])
    
    players = {}
    for player in players_list:
        player_id = player.get('id')
        if player_id:
            players[player_id] = {
                'id': player_id,
                'name': player.get('fullname'),
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
    
    # If no players found in squad, try to get players from recent matches
    if not players:
        print(f"No squad data found for {team_name}, trying to get players from recent matches...")
        fixtures_url = "https://cricket.sportmonks.com/api/v2.0/fixtures"
        fixtures_params = {
            "api_token": API_TOKEN,
            "filter[type]": "T20I",
            "filter[status]": "Finished",
            "$or[localteam_id]": team_id,
            "$or[visitorteam_id]": team_id,
            "include": "localteam,visitorteam,batting.batsman,bowling.bowler",
            "sort": "-starting_at",
            "per_page": 5
        }
        
        fixtures_response = make_request(fixtures_url, fixtures_params)
        if fixtures_response and fixtures_response.status_code == 200:
            matches = fixtures_response.json().get('data', [])
            for match in matches:
                # Process batting
                batting = match.get('batting', [])
                for innings in batting:
                    if innings.get('team_id') == team_id:
                        batsman = innings.get('batsman', {})
                        player_id = batsman.get('id')
                        if player_id and player_id not in players:
                            players[player_id] = {
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
                
                # Process bowling
                bowling = match.get('bowling', [])
                for spell in bowling:
                    if spell.get('team_id') == team_id:
                        bowler = spell.get('bowler', {})
                        player_id = bowler.get('id')
                        if player_id and player_id not in players:
                            players[player_id] = {
                                'id': player_id,
                                'name': bowler.get('fullname'),
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
    
    return players

def get_recent_t20i_performances(team_id):
    """Get recent T20I performances for specified team's players"""
    if team_id is None:
        return None
        
    team_name = get_team_name(team_id)
    if not team_name:
        print(f"Could not find team with ID {team_id}")
        return None
    
    print(f"Getting {team_name} team data...")
    
    # Get recent T20I fixtures where team was either local or visitor team
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
            "per_page": 20  # Get more matches to filter team's matches
        }
        
        print("\nTrying alternative approach...")
        fixtures_response = make_request(fixtures_url, fixtures_params)
        if not fixtures_response or fixtures_response.status_code != 200:
            return None
    
    matches = fixtures_response.json().get('data', [])
    
    # Filter matches where team played
    team_matches = []
    for match in matches:
        local_team = match.get('localteam', {}).get('id')
        visitor_team = match.get('visitorteam', {}).get('id')
        
        if team_id in [local_team, visitor_team]:
            team_matches.append(match)
            if len(team_matches) >= 5:  # Only get last 5 matches
                break
    
    print(f"\nFound {len(team_matches)} {team_name} T20I matches")
    
    # Collect player performances
    player_performances = {}
    
    for match in team_matches:
        match_date = match.get('starting_at')
        print(f"\nProcessing match from {match_date}")
        local_team = match.get('localteam', {})
        visitor_team = match.get('visitorteam', {})
        print(f"{local_team.get('name')} vs {visitor_team.get('name')}")
        
        # Determine which team is our target team
        is_team_local = local_team.get('id') == team_id
        team_team_id = local_team.get('id') if is_team_local else visitor_team.get('id')
        
        # Process batting performances
        batting = match.get('batting', [])
        for innings in batting:
            if innings.get('team_id') == team_team_id:
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
                            'highest': 0,
                            'not_outs': 0
                        },
                        'bowling': {
                            'innings': 0,
                            'overs': 0,
                            'wickets': 0,
                            'runs': 0,
                            'best': '0/0',
                            'maidens': 0
                        }
                    }
                
                perf = player_performances[player_id]
                perf['matches'] += 1
                perf['batting']['innings'] += 1
                perf['batting']['runs'] += innings.get('score', 0)
                perf['batting']['balls'] += innings.get('ball', 0)
                perf['batting']['fours'] += innings.get('four_x', 0)
                perf['batting']['sixes'] += innings.get('six_x', 0)
                perf['batting']['not_outs'] += 1 if innings.get('out', False) else 0
                
                score = innings.get('score', 0)
                if score > perf['batting']['highest']:
                    perf['batting']['highest'] = score
        
        # Process bowling performances
        bowling = match.get('bowling', [])
        for spell in bowling:
            if spell.get('team_id') == team_team_id:
                bowler = spell.get('bowler', {})
                player_id = bowler.get('id')
                
                if player_id not in player_performances:
                    player_performances[player_id] = {
                        'id': player_id,
                        'name': bowler.get('fullname'),
                        'matches': 0,
                        'batting': {
                            'innings': 0,
                            'runs': 0,
                            'balls': 0,
                            'fours': 0,
                            'sixes': 0,
                            'highest': 0,
                            'not_outs': 0
                        },
                        'bowling': {
                            'innings': 0,
                            'overs': 0,
                            'wickets': 0,
                            'runs': 0,
                            'best': '0/0',
                            'maidens': 0
                        }
                    }
                
                perf = player_performances[player_id]
                perf['bowling']['innings'] += 1
                perf['bowling']['overs'] += spell.get('overs', 0)
                perf['bowling']['wickets'] += spell.get('wickets', 0)
                perf['bowling']['runs'] += spell.get('runs', 0)
                perf['bowling']['maidens'] += spell.get('maidens', 0)
                
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

def get_player_position(player_id):
    """Get player's position from the positions API"""
    # First get all positions
    positions_url = "https://cricket.sportmonks.com/api/v2.0/positions"
    positions_params = {
        "api_token": API_TOKEN
    }
    
    response = make_request(positions_url, positions_params)
    if response and response.status_code == 200:
        positions_data = response.json()
        if positions_data.get('data'):
            # Create a mapping of position IDs to names
            position_map = {pos['id']: pos['name'] for pos in positions_data['data']}
            
            # Now get player's position
            player_url = f"https://cricket.sportmonks.com/api/v2.0/players/{player_id}"
            player_params = {
                "api_token": API_TOKEN,
                "include": "career"
            }
            
            player_response = make_request(player_url, player_params)
            if player_response and player_response.status_code == 200:
                player_data = player_response.json()
                if player_data.get('data'):
                    # Get position ID from player data
                    position_id = player_data['data'].get('position_id')
                    if position_id in position_map:
                        position = position_map[position_id]
                        
                        # Special case for wicketkeeper-batsmen
                        if position == "Batsman" and "wicketkeeper" in player_data['data'].get('fullname', '').lower():
                            return "Wicketkeeper"
                        return position
    
    return None

def calculate_player_rating(player):
    """Calculate a player's rating based on recent performances"""
    batting_stats = player['batting']
    bowling_stats = player['bowling']
    
    # Calculate batting rating
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
    
    # Calculate bowling rating
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
    
    # Calculate overall rating
    overall_rating = max(batting_rating, bowling_rating)
    if batting_rating > 0 and bowling_rating > 0:
        overall_rating = (batting_rating + bowling_rating) / 2
    
    return {
        'name': player['name'],
        'batting_rating': batting_rating,
        'bowling_rating': bowling_rating,
        'overall_rating': overall_rating,
        'batting': batting_stats,
        'bowling': bowling_stats
    }

def predict_best_xi(performances):
    """Predict the best XI based on recent performances"""
    # Create rated players with their performance data
    rated_players = []
    for player_id, player_data in performances.items():
        player_data['id'] = player_id
        rating = calculate_player_rating(player_data)
        rated_players.append(rating)
    
    # Sort all players by overall rating
    rated_players.sort(key=lambda x: x['overall_rating'], reverse=True)
    
    # Select top 11 players
    best_xi = rated_players[:11]
    
    # Remaining players go to bench strength
    bench_strength = rated_players[11:]
    
    return {
        'players': best_xi,
        'total_rating': sum(p['overall_rating'] for p in best_xi) / len(best_xi) if best_xi else 0,
        'bench_strength': bench_strength
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
        for player in best_xi['players']:
            print(f"{player['name']} - Rating: {player['overall_rating']:.1f}")
        
        print(f"\nTeam Rating: {best_xi['total_rating']:.1f}")
        
        # Verify team composition
        total_players = len(best_xi['players'])
        print(f"\nTotal players selected: {total_players}")
    else:
        print("Failed to collect performance data") 