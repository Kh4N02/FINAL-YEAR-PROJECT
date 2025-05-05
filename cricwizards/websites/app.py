from flask import Flask, render_template, jsonify, request
import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.get_pakistan_t20 import get_recent_t20i_performances, predict_best_xi

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/predict')
# def predict():
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        team_id = request.form.get('team_id')
        try:
            performances = get_recent_t20i_performances(team_id=team_id)
            if performances:
                best_xi = predict_best_xi(performances)
                trends = analyze_performance_trends(performances)
                return render_template('predict.html', 
                                     team=best_xi, 
                                     trends=trends)
            return render_template('error.html', message="No data available")
        except Exception as e:
            return render_template('error.html', message=str(e))
    return render_template('index.html')

@app.route('/performance')
def performance():
    try:
        performances = get_recent_t20i_performances()
        if performances:
            # Convert performances to DataFrame for analysis
            df = pd.DataFrame(performances.values())
            
            # Calculate performance metrics
            batting_stats = calculate_batting_stats(df)
            bowling_stats = calculate_bowling_stats(df)
            allrounder_stats = calculate_allrounder_stats(df)
            
            return render_template('performance.html',
                                 batting_stats=batting_stats,
                                 bowling_stats=bowling_stats,
                                 allrounder_stats=allrounder_stats)
        return render_template('error.html', message="No performance data available")
    except Exception as e:
        return render_template('error.html', message=str(e))

def analyze_performance_trends(performances):
    """Analyze recent performance trends"""
    trends = {
        'form_players': [],
        'recent_performances': [],
        'team_balance': {
            'batsmen': 0,
            'bowlers': 0,
            'all_rounders': 0,
            'wicketkeepers': 0
        }
    }
    
    for player in performances.values():
        # Analyze recent form
        if player['batting']['innings'] > 0:
            avg = player['batting']['runs'] / player['batting']['innings']
            if avg > 30:
                trends['form_players'].append({
                    'name': player['name'],
                    'type': 'Batting',
                    'stat': f"Avg: {avg:.2f}"
                })
                
        if player['bowling']['innings'] > 0:
            wickets = player['bowling']['wickets']
            if wickets > 3:
                trends['form_players'].append({
                    'name': player['name'],
                    'type': 'Bowling',
                    'stat': f"Wickets: {wickets}"
                })
    
    return trends

def calculate_batting_stats(df):
    """Calculate detailed batting statistics"""
    stats = []
    for _, player in df.iterrows():
        if player['batting']['innings'] > 0:
            stats.append({
                'name': player['name'],
                'matches': player['matches'],
                'runs': player['batting']['runs'],
                'average': player['batting']['runs'] / player['batting']['innings'],
                'strike_rate': (player['batting']['runs'] / player['batting']['balls'] * 100) 
                              if player['batting']['balls'] > 0 else 0,
                'highest': player['batting']['highest']
            })
    return sorted(stats, key=lambda x: x['runs'], reverse=True)

def calculate_bowling_stats(df):
    """Calculate detailed bowling statistics"""
    stats = []
    for _, player in df.iterrows():
        if player['bowling']['innings'] > 0:
            stats.append({
                'name': player['name'],
                'matches': player['matches'],
                'wickets': player['bowling']['wickets'],
                'economy': player['bowling']['runs'] / player['bowling']['overs'] 
                          if player['bowling']['overs'] > 0 else 0,
                'best': player['bowling']['best']
            })
    return sorted(stats, key=lambda x: x['wickets'], reverse=True)

def calculate_allrounder_stats(df):
    """Calculate statistics for players who both bat and bowl"""
    stats = []
    for _, player in df.iterrows():
        # Check if player has both batting and bowling performances
        if (player['batting']['innings'] > 0 and 
            player['bowling']['innings'] > 0):
            stats.append({
                'name': player['name'],
                'matches': player['matches'],
                # Batting stats
                'runs': player['batting']['runs'],
                'batting_average': player['batting']['runs'] / player['batting']['innings'],
                'strike_rate': (player['batting']['runs'] / player['batting']['balls'] * 100) 
                              if player['batting']['balls'] > 0 else 0,
                # Bowling stats
                'wickets': player['bowling']['wickets'],
                'economy': player['bowling']['runs'] / player['bowling']['overs'] 
                          if player['bowling']['overs'] > 0 else 0,
                'bowling_average': (player['bowling']['runs'] / player['bowling']['wickets'] 
                                  if player['bowling']['wickets'] > 0 else float('inf')),
                # Combined rating
                'all_round_rating': calculate_all_round_rating(player)
            })
    return sorted(stats, key=lambda x: x['all_round_rating'], reverse=True)

def calculate_all_round_rating(player):
    """Calculate a combined rating for all-rounders"""
    batting_points = (
        (player['batting']['runs'] / player['batting']['innings'] * 2) +  # Weight for average
        (player['batting']['fours'] + player['batting']['sixes'])         # Boundary bonus
    ) if player['batting']['innings'] > 0 else 0
    
    bowling_points = (
        (player['bowling']['wickets'] * 20) +                            # Points per wicket
        (player['bowling']['overs'] * 2)                                 # Points for bowling overs
    ) if player['bowling']['innings'] > 0 else 0
    
    return batting_points + bowling_points

if __name__ == '__main__':
    app.run(debug=True)