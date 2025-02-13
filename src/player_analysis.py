class PlayerAnalyzer:
    def __init__(self):
        self.performance_weights = {
            'batting_average': 0.3,
            'strike_rate': 0.2,
            'bowling_average': 0.25,
            'economy_rate': 0.25
        }
    
    def calculate_player_score(self, player_stats):
        # Basic scoring algorithm
        score = 0
        if player_stats.get('batting'):
            batting_score = (
                float(player_stats['batting'].get('average', 0)) * self.performance_weights['batting_average'] +
                float(player_stats['batting'].get('strike_rate', 0)) * self.performance_weights['strike_rate']
            )
            score += batting_score
            
        if player_stats.get('bowling'):
            bowling_score = (
                (1/float(player_stats['bowling'].get('average', 1))) * self.performance_weights['bowling_average'] +
                (1/float(player_stats['bowling'].get('economy', 1))) * self.performance_weights['economy_rate']
            )
            score += bowling_score
            
        return score 