import pandas as pd

class DataProcessor:
    def __init__(self, cricket_api):
        self.cricket_api = cricket_api
        
    def get_team_data(self, team_id):
        team_data = self.cricket_api.get_team_players(team_id)
        players_data = []
        
        for player in team_data['data']['squad']:
            player_stats = self.cricket_api.get_player_stats(player['id'])
            players_data.append({
                'id': player['id'],
                'name': player['fullname'],
                'role': player.get('position', {}).get('name', 'Unknown'),
                'stats': player_stats['data'].get('career', {})
            })
            
        return pd.DataFrame(players_data) 