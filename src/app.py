from flask import Flask, render_template, request
from cricket_api import CricketAPI
from data_processor import DataProcessor
from player_analysis import PlayerAnalyzer
from prediction_model import TeamPredictor

app = Flask(__name__)

cricket_api = CricketAPI()
data_processor = DataProcessor(cricket_api)
player_analyzer = PlayerAnalyzer()
team_predictor = TeamPredictor(player_analyzer)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    team_id = request.form['team_id']
    print(f"Fetching data for team ID: {team_id}")
    
    players_df = data_processor.get_team_data(team_id)
    print(f"Found {len(players_df)} players")
    
    best_xi = team_predictor.predict_best_xi(players_df)
    print(f"Selected best XI: {[player['name'] for player in best_xi]}")
    
    return render_template('result.html', team=best_xi)

if __name__ == '__main__':
    app.run(debug=True) 