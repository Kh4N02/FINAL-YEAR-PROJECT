from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from functools import wraps
import requests

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.get_team_performances import (
    get_recent_t20i_performances,
    predict_best_xi,
    get_team_name,
    calculate_player_rating,
    API_TOKEN
)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cricwizards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

def get_teams():
    """Get the list of teams with their flags"""
    return [
        {'id': 36, 'name': 'Australia', 'flag': '🇦🇺'},
        {'id': 38, 'name': 'England', 'flag': url_for('static', filename='images/flags/england_flag.png')},
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

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    # Clear the team_id from session when returning to home
    session.pop('team_id', None)
    return render_template('index.html', teams=get_teams())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not User.validate_username(username):
            flash('Username must be 3-20 characters and contain only letters, numbers, and underscores.', 'danger')
            return render_template('register.html')
            
        if not User.validate_password(password):
            flash('Password must be at least 8 characters and contain uppercase, lowercase, number, and special character.', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
            
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
            
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return render_template('register.html')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Welcome back!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    try:
        # Get team_id from either POST data, URL parameters, or session
        team_id = None
        if request.method == 'POST':
            team_id = request.form.get('team_id')
        else:
            team_id = request.args.get('team_id') or session.get('team_id')
        
        if not team_id:
            return redirect(url_for('home'))
        
        # Store team_id in session
        session['team_id'] = team_id
        
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
        rated_players = []
        for player_id, player_data in performances.items():
            player_data['id'] = player_id
            rating = calculate_player_rating(player_data)
            rated_players.append(rating)
        
        # Predict best XI
        best_xi = predict_best_xi(performances)
        
        # Fetch player images for best XI
        for player in best_xi['players']:
            try:
                player_url = f"https://cricket.sportmonks.com/api/v2.0/players/{player['id']}"
                params = {"api_token": API_TOKEN}
                response = requests.get(player_url, params=params)
                if response.status_code == 200:
                    player_data = response.json().get('data')
                    if player_data:
                        player['image_path'] = player_data.get('image_path')
            except Exception as e:
                print(f"Error fetching image for player {player['name']}: {str(e)}")
                player['image_path'] = None
        
        # Fetch player images for bench strength
        for player in best_xi['bench_strength']:
            try:
                player_url = f"https://cricket.sportmonks.com/api/v2.0/players/{player['id']}"
                params = {"api_token": API_TOKEN}
                response = requests.get(player_url, params=params)
                if response.status_code == 200:
                    player_data = response.json().get('data')
                    if player_data:
                        player['image_path'] = player_data.get('image_path')
            except Exception as e:
                print(f"Error fetching image for player {player['name']}: {str(e)}")
                player['image_path'] = None
            
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
@login_required
def performance():
    team_id = request.args.get('team_id') or session.get('team_id')
    
    if not team_id:
        return redirect(url_for('home'))
        
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
        
        # Prepare all players data for comparison dropdowns
        all_players = []
        for player_id, player_data in performances.items():
            player_stats = {
                'id': player_id,
                'name': player_data['name'],
                'batting': player_data['batting'],
                'bowling': player_data['bowling'],
                'matches': player_data['matches']
            }
            all_players.append(player_stats)
        
        team_name = get_team_name(int(team_id))
        if not team_name:
            return render_template('error.html', 
                                 message=f"Could not find team information for ID: {team_id}")
        
        return render_template('performance.html',
                             batting_stats=batting_stats,
                             bowling_stats=bowling_stats,
                             allrounder_stats=allrounder_stats,
                             all_players=all_players,
                             team_name=team_name)
                             
    except Exception as e:
        print(f"Error processing team {team_id}: {str(e)}")
        return render_template('error.html', 
                             message=f"An error occurred while processing the team data: {str(e)}")

@app.route('/compare_players', methods=['POST'])
@login_required
def compare_players():
    try:
        player1_name = request.form.get('player1')
        player2_name = request.form.get('player2')
        team_id = session.get('team_id')
        
        if not team_id:
            return jsonify({'error': 'No team selected'})
            
        performances = get_recent_t20i_performances(int(team_id))
        if not performances:
            return jsonify({'error': 'No performance data available'})
            
        # Find players by name instead of ID
        player1_data = next((p for p in performances.values() if p['name'] == player1_name), None)
        player2_data = next((p for p in performances.values() if p['name'] == player2_name), None)
        
        if not player1_data or not player2_data:
            return jsonify({'error': 'Player data not found'})
            
        comparison = {
            'player1': {
                'name': player1_data['name'],
                'batting': player1_data['batting'],
                'bowling': player1_data['bowling'],
                'matches': player1_data['matches']
            },
            'player2': {
                'name': player2_data['name'],
                'batting': player2_data['batting'],
                'bowling': player2_data['bowling'],
                'matches': player2_data['matches']
            }
        }
        
        return jsonify(comparison)
        
    except Exception as e:
        return jsonify({'error': str(e)})

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
                'id': player['id'],  # Add player ID
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
            # Calculate bowling average, use '∞' for infinite
            bowling_avg = '∞' if player['bowling']['wickets'] == 0 else (
                player['bowling']['runs'] / player['bowling']['wickets']
            )
            
            stats.append({
                'id': player['id'],  # Add player ID
                'name': player['name'],
                'matches': player['matches'],
                'wickets': player['bowling']['wickets'],
                'economy': player['bowling']['runs'] / player['bowling']['overs'] 
                          if player['bowling']['overs'] > 0 else 0,
                'bowling_average': bowling_avg,
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
            # Calculate bowling average, use '∞' for infinite
            bowling_avg = '∞' if player['bowling']['wickets'] == 0 else (
                player['bowling']['runs'] / player['bowling']['wickets']
            )
            
            stats.append({
                'id': player['id'],  # Add player ID
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
                'bowling_average': bowling_avg,
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

@app.route('/player/<int:player_id>')
@login_required
def player_profile(player_id):
    try:
        print(f"Fetching data for player ID: {player_id}")
        
        # Get player data from API - simplified to match working Postman request
        player_url = f"https://cricket.sportmonks.com/api/v2.0/players/{player_id}"
        params = {
            "api_token": API_TOKEN
        }
        
        print(f"Making request to: {player_url}")
        print(f"With params: {params}")
        
        response = requests.get(player_url, params=params)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:500]}")  # Print first 500 chars of response
        
        if response.status_code != 200:
            return render_template('error.html', message=f"Could not fetch player data. Status code: {response.status_code}")
            
        player_data = response.json().get('data')
        if not player_data:
            return render_template('error.html', message="Player not found in API response")
            
        # Get recent performances
        team_id = session.get('team_id')
        if not team_id:
            return render_template('error.html', message="No team selected")
            
        performances = get_recent_t20i_performances(int(team_id))
        if not performances:
            return render_template('error.html', message="Could not fetch recent performances")
            
        player_performance = next((p for p in performances.values() if p['id'] == player_id), None)
        
        # Initialize career stats with zeros
        career_stats = {
            'batting': {
                'matches': 0,
                'innings': 0,
                'runs': 0,
                'average': 0,
                'strike_rate': 0,
                'highest': 0
            },
            'bowling': {
                'matches': 0,
                'innings': 0,
                'wickets': 0,
                'average': '∞',  # Changed to string '∞'
                'economy': 0,
                'best': '0/0'
            }
        }
        
        # If we have recent performance data, use that for stats
        if player_performance:
            career_stats['batting'].update({
                'matches': player_performance['matches'],
                'innings': player_performance['batting']['innings'],
                'runs': player_performance['batting']['runs'],
                'average': player_performance['batting']['runs'] / player_performance['batting']['innings'] if player_performance['batting']['innings'] > 0 else 0,
                'strike_rate': (player_performance['batting']['runs'] / player_performance['batting']['balls'] * 100) if player_performance['batting']['balls'] > 0 else 0,
                'highest': player_performance['batting']['highest']
            })
            
            career_stats['bowling'].update({
                'matches': player_performance['matches'],
                'innings': player_performance['bowling']['innings'],
                'wickets': player_performance['bowling']['wickets'],
                'average': '∞' if player_performance['bowling']['wickets'] == 0 else (
                    player_performance['bowling']['runs'] / player_performance['bowling']['wickets']
                ),
                'economy': player_performance['bowling']['runs'] / player_performance['bowling']['overs'] if player_performance['bowling']['overs'] > 0 else 0,
                'best': player_performance['bowling']['best']
            })
        
        return render_template('player_profile.html',
                             player=player_data,
                             career_stats=career_stats,
                             recent_performance=player_performance)
                             
    except Exception as e:
        print(f"Error in player profile: {str(e)}")
        return render_template('error.html', message=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)