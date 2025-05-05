import os
from src.get_team_performances import (
    get_recent_t20i_performances,
    predict_best_xi,
    get_team_name,
    calculate_player_rating,
    API_TOKEN
)

def generate_performance_html():
    """Generate static performance.html with real data"""
    print("Fetching Pakistan T20I performance data...")
    
    # Get real data
    performances = get_recent_t20i_performances()
    
    if not performances:
        print("Failed to get performance data")
        return
    
    # Save the data for reference
    save_performances(performances)
    
    # Get best XI prediction
    best_xi = predict_best_xi(performances)
    
    # Process players data
    all_rounders = []
    batsmen = []
    bowlers = []
    
    for player_id, player in performances.items():
        # Get player rating and role
        rating_info = calculate_player_rating(player)
        role = rating_info['role']
        
        # Calculate match count correctly from the API data
        matches = player['matches']
        
        # Process batting stats
        batting_stats = player['batting']
        batting_inns = batting_stats['innings']
        batting_runs = batting_stats['runs']
        batting_avg = batting_runs / batting_inns if batting_inns > 0 else 0
        strike_rate = (batting_runs / batting_stats['balls'] * 100) if batting_stats['balls'] > 0 else 0
        
        # Process bowling stats
        bowling_stats = player['bowling']
        bowling_inns = bowling_stats['innings']
        wickets = bowling_stats['wickets']
        economy = bowling_stats['runs'] / bowling_stats['overs'] if bowling_stats['overs'] > 0 else 0
        
        # Add player to appropriate list based on their role
        if role == "All-rounder" or (batting_inns > 0 and bowling_inns > 0):
            all_rounders.append({
                'name': player['name'],
                'matches': matches,
                'runs': batting_runs,
                'batting_avg': batting_avg,
                'strike_rate': strike_rate,
                'wickets': wickets,
                'economy': economy,
                'rating': rating_info['overall_rating']
            })
        elif role == "Batsman" or batting_inns > 0:
            batsmen.append({
                'name': player['name'],
                'matches': matches,
                'runs': batting_runs,
                'average': batting_avg,
                'strike_rate': strike_rate,
                'highest': batting_stats['highest']
            })
        elif role == "Bowler" or bowling_inns > 0:
            bowlers.append({
                'name': player['name'],
                'matches': matches,
                'wickets': wickets,
                'economy': economy,
                'best': bowling_stats['best']
            })
    
    # Sort lists
    all_rounders.sort(key=lambda x: x['rating'], reverse=True)
    batsmen.sort(key=lambda x: x['runs'], reverse=True)
    bowlers.sort(key=lambda x: x['wickets'], reverse=True)
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CricWizards XI - Performance Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="../static/css/styles.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="../../index.html">CricWizards XI</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="../../index.html">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="predict.html">Predict XI</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="performance.html">Performance Analysis</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container py-4">
        <div class="performance-analysis">
            <h1 class="mb-4">Performance Analysis</h1>
            
            <!-- All-Rounders Section -->
            <div class="card mb-4">
                <div class="card-header bg-warning text-dark">
                    <h2 class="h5 mb-0">All-Round Performances</h2>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Player</th>
                                    <th>Matches</th>
                                    <th>Runs</th>
                                    <th>Bat Avg</th>
                                    <th>SR</th>
                                    <th>Wickets</th>
                                    <th>Economy</th>
                                    <th>Rating</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(f'''
                                <tr>
                                    <td>{p['name']}</td>
                                    <td>{p['matches']}</td>
                                    <td>{p['runs']}</td>
                                    <td>{p['batting_avg']:.2f}</td>
                                    <td>{p['strike_rate']:.2f}</td>
                                    <td>{p['wickets']}</td>
                                    <td>{p['economy']:.2f}</td>
                                    <td>{p['rating']:.1f}</td>
                                </tr>''' for p in all_rounders)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Batting Section -->
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h2 class="h5 mb-0">Batting Performances</h2>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Player</th>
                                    <th>Matches</th>
                                    <th>Runs</th>
                                    <th>Average</th>
                                    <th>Strike Rate</th>
                                    <th>Highest Score</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(f'''
                                <tr>
                                    <td>{p['name']}</td>
                                    <td>{p['matches']}</td>
                                    <td>{p['runs']}</td>
                                    <td>{p['average']:.2f}</td>
                                    <td>{p['strike_rate']:.2f}</td>
                                    <td>{p['highest']}</td>
                                </tr>''' for p in batsmen)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Bowling Section -->
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h2 class="h5 mb-0">Bowling Performances</h2>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Player</th>
                                    <th>Matches</th>
                                    <th>Wickets</th>
                                    <th>Economy</th>
                                    <th>Best Figures</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(f'''
                                <tr>
                                    <td>{p['name']}</td>
                                    <td>{p['matches']}</td>
                                    <td>{p['wickets']}</td>
                                    <td>{p['economy']:.2f}</td>
                                    <td>{p['best']}</td>
                                </tr>''' for p in bowlers)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    
    # Write to file
    with open('website/templates/performance.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Generated performance.html with real data")
    
    # Also generate predict.html with the best XI
    generate_predict_html(best_xi)

def generate_predict_html(best_xi):
    """Generate static predict.html with best XI data"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CricWizards XI - Best XI Prediction</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="../static/css/styles.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="../../index.html">CricWizards XI</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="../../index.html">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="predict.html">Predict XI</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="performance.html">Performance Analysis</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container py-4">
        <div class="best-xi">
            <h1 class="mb-4">Predicted Best XI</h1>
            
            <div class="row">
                <!-- Wicketkeeper Section -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-info text-white">
                            <h2 class="h5 mb-0">Wicketkeeper</h2>
                        </div>
                        <div class="card-body">
                            {''.join(f'''
                            <div class="player-item">
                                <h3>{p['name']}</h3>
                                <p>Batting Rating: {p['batting_rating']:.1f}</p>
                            </div>''' for p in best_xi['wicketkeeper'])}
                        </div>
                    </div>
                </div>

                <!-- Batsmen Section -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h2 class="h5 mb-0">Batsmen</h2>
                        </div>
                        <div class="card-body">
                            {''.join(f'''
                            <div class="player-item">
                                <h3>{p['name']}</h3>
                                <p>Batting Rating: {p['batting_rating']:.1f}</p>
                            </div>''' for p in best_xi['batsmen'])}
                        </div>
                    </div>
                </div>

                <!-- All-rounders Section -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-warning text-dark">
                            <h2 class="h5 mb-0">All-rounders</h2>
                        </div>
                        <div class="card-body">
                            {''.join(f'''
                            <div class="player-item">
                                <h3>{p['name']}</h3>
                                <p>Batting: {p['batting_rating']:.1f}, Bowling: {p['bowling_rating']:.1f}</p>
                            </div>''' for p in best_xi['allrounders'])}
                        </div>
                    </div>
                </div>

                <!-- Bowlers Section -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h2 class="h5 mb-0">Bowlers</h2>
                        </div>
                        <div class="card-body">
                            {''.join(f'''
                            <div class="player-item">
                                <h3>{p['name']}</h3>
                                <p>Bowling Rating: {p['bowling_rating']:.1f}</p>
                            </div>''' for p in best_xi['bowlers'])}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="team-rating mt-4">
                <h3>Team Rating: {best_xi['total_rating']:.1f}</h3>
            </div>
        </div>
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    
    with open('website/templates/predict.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Generated predict.html with best XI data")

if __name__ == "__main__":
    generate_performance_html() 