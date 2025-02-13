import unittest
from src.player_analysis import PlayerAnalyzer
from src.prediction_model import TeamPredictor

class TestPrediction(unittest.TestCase):
    def setUp(self):
        self.player_analyzer = PlayerAnalyzer()
        self.team_predictor = TeamPredictor(self.player_analyzer)
    
    def test_player_score_calculation(self):
        test_stats = {
            'batting': {'average': 45.5, 'strike_rate': 135.6},
            'bowling': {'average': 25.3, 'economy': 6.8}
        }
        score = self.player_analyzer.calculate_player_score(test_stats)
        self.assertIsInstance(score, float) 