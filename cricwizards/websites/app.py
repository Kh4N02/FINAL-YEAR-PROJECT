from flask import Flask, render_template, jsonify, request
import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.get_pakistan_t20 import (
    get_recent_t20i_performances,
    predict_best_xi,
    get_team_name,
    calculate_player_rating
)

app = Flask(__name__)

# Define teams data
TEAMS = [
    {'id': 36, 'name': 'Australia', 'flag': '🇦🇺'},
    {'id': 38, 'name': 'England', 'flag': '🇬🇧'},
    {'id': 40, 'name': 'South Africa', 'flag': '🇿🇦'},
    {'id': 10, 'name': 'India', 'flag': '🇮🇳'},
    {'id': 42, 'name': 'New Zealand', 'flag': '🇳🇿'},
    {'id': 39, 'name': 'Sri Lanka', 'flag': '🇱🇰'},
    {'id': 1,  'name': 'Pakistan', 'flag': '🇵🇰'},
    {'id': 43, 'name': 'West Indies', 'flag': '🇻🇨'},
    {'id': 37, 'name': 'Bangladesh', 'flag': '🇧🇩'},
    {'id': 100,'name': 'Ireland', 'flag': '🇮🇪'},
    {'id': 46, 'name': 'Afghanistan', 'flag': '🇦🇫'},
    {'id': 41, 'name': 'Zimbabwe', 'flag': '🇿🇼'}
]

@app.route('/')
def home():
    return render_template('index.html', teams=TEAMS)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        team_id = request.form.get('team_id')
        if not team_id:
            return render_template('error.html', message="No team selected")
        
        print(f"Fetching data for team ID: {team_id}")
        
        # Get team name first
        team_name = get_team_name(int(team_id))
        if not team_name:
            return render_template('error.html', message=f"Could not find team with ID {team_id}")
        
        # Get player performances
        performances = get_recent_t20i_performances(int(team_id))
        if not performances:
            return render_template('error.html', message=f"No performance data available for {team_name}")
        
        # Calculate player ratings
        rated_players = [calculate_player_rating(player) for player in performances.values()]
        
        # Predict best XI
        best_xi = predict_best_xi(performances)
            
        # Calculate team stats
        team_stats = calculate_team_stats(performances)
            
        return render_template('predict.html', 
                             team_name=team_name,
                             best_xi=best_xi,
                             team_stats=team_stats)
                             
    except Exception as e:
        print(f"Error in predict route: {str(e)}")
        return render_template('error.html', 
                             message=f"An error occurred while processing the team data: {str(e)}")

@app.route('/performance')
def performance():
    team_id = request.args.get('team_id')
    if not team_id:
        return render_template('error.html', message="No team selected")
        
    try:
        print(f"Fetching performance data for team ID: {team_id}")
        performances = get_recent_t20i_performances(int(team_id))
        
        if not performances:
            return render_template('error.html', 
                                 message=f"No recent performance data available for this team. Please try another team.")
        
            # Convert performances to DataFrame for analysis
            df = pd.DataFrame(performances.values())
            
            # Calculate performance metrics
            batting_stats = calculate_batting_stats(df)
            bowling_stats = calculate_bowling_stats(df)
            allrounder_stats = calculate_allrounder_stats(df)
            
        team_name = get_team_name(int(team_id))
        if not team_name:
            return render_template('error.html', 
                                 message=f"Could not find team information for ID: {team_id}")
        
            return render_template('performance.html',
                                 batting_stats=batting_stats,
                                 bowling_stats=bowling_stats,
                             allrounder_stats=allrounder_stats,
                             team_name=team_name)
                             
    except ValueError as e:
        return render_template('error.html', 
                             message=f"Invalid team ID: {team_id}")
    except Exception as e:
        print(f"Error processing team {team_id}: {str(e)}")
        return render_template('error.html', 
                             message=f"An error occurred while processing the team data: {str(e)}")

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

def calculate_team_stats(performances):
    """Calculate overall team statistics"""
    stats = {
        'total_players': len(performances),
        'batting': {
            'total_runs': 0,
            'total_innings': 0,
            'total_balls': 0,
            'total_fours': 0,
            'total_sixes': 0
        },
        'bowling': {
            'total_wickets': 0,
            'total_overs': 0,
            'total_runs': 0
        }
    }
    
    for player in performances.values():
        # Batting stats
        stats['batting']['total_runs'] += player['batting']['runs']
        stats['batting']['total_innings'] += player['batting']['innings']
        stats['batting']['total_balls'] += player['batting']['balls']
        stats['batting']['total_fours'] += player['batting']['fours']
        stats['batting']['total_sixes'] += player['batting']['sixes']
        
        # Bowling stats
        stats['bowling']['total_wickets'] += player['bowling']['wickets']
        stats['bowling']['total_overs'] += player['bowling']['overs']
        stats['bowling']['total_runs'] += player['bowling']['runs']
    
    # Calculate averages and rates
    if stats['batting']['total_innings'] > 0:
        stats['batting']['average'] = stats['batting']['total_runs'] / stats['batting']['total_innings']
    else:
        stats['batting']['average'] = 0
        
    if stats['batting']['total_balls'] > 0:
        stats['batting']['strike_rate'] = (stats['batting']['total_runs'] / stats['batting']['total_balls']) * 100
    else:
        stats['batting']['strike_rate'] = 0
        
    if stats['bowling']['total_overs'] > 0:
        stats['bowling']['economy_rate'] = stats['bowling']['total_runs'] / stats['bowling']['total_overs']
    else:
        stats['bowling']['economy_rate'] = 0
        
    if stats['bowling']['total_wickets'] > 0:
        stats['bowling']['bowling_average'] = stats['bowling']['total_runs'] / stats['bowling']['total_wickets']
    else:
        stats['bowling']['bowling_average'] = 0
    
    return stats

if __name__ == '__main__':
    app.run(debug=True)