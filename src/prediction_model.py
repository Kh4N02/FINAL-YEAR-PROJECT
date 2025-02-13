from sklearn.ensemble import RandomForestClassifier
import numpy as np

class TeamPredictor:
    def __init__(self, player_analyzer):
        self.player_analyzer = player_analyzer
        self.model = RandomForestClassifier()
        
    def predict_best_xi(self, players_df):
        # Calculate scores for all players
        scores = []
        for _, player in players_df.iterrows():
            score = self.player_analyzer.calculate_player_score(player['stats'])
            scores.append(score)
            
        # Sort players by score and ensure team balance
        players_df['score'] = scores
        best_xi = self.select_balanced_team(players_df)
        return best_xi
        
    def select_balanced_team(self, players_df):
        # Basic team composition rules
        required_composition = {
            'Batsman': 6,
            'Bowler': 4,
            'All-rounder': 1
        }
        
        best_xi = []
        for role, count in required_composition.items():
            role_players = players_df[players_df['role'] == role].nlargest(count, 'score')
            best_xi.extend(role_players.to_dict('records'))
            
        return best_xi 