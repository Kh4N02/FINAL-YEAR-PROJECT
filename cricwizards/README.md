# CricWizards XI

Advanced cricket analytics platform for ICC T20I team selection and performance analysis.

## Overview

CricWizards XI is a web application that provides advanced analytics and insights for T20I cricket teams. It helps in:
- Analyzing player performances
- Predicting the best XI for teams
- Comparing player statistics
- Viewing detailed player profiles
- Making data-driven team selection decisions

## Features

- **Team Selection**: Choose from multiple ICC T20I teams
- **Performance Analysis**: Detailed batting, bowling, and all-rounder statistics
- **Player Comparison**: Compare any two players' statistics
- **Best XI Prediction**: AI-powered team selection based on recent performances
- **Player Profiles**: Comprehensive player statistics and career information
- **User Authentication**: Secure login and registration system

## Technical Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite
- **API**: Cricket API (SportMonks)
- **Authentication**: Flask-SQLAlchemy, Werkzeug

## Installation

### Option 1: Direct Installation (Local Development)
1. Clone the repository:
```bash
git clone https://github.com/Kh4N02/FINAL-YEAR-PROJECT.git
cd FINAL-YEAR-PROJECT
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python websites/app.py
```

### Option 2: Using Virtual Environment (Recommended for Production)
1. Clone the repository:
```bash
git clone https://github.com/Kh4N02/FINAL-YEAR-PROJECT.git
cd FINAL-YEAR-PROJECT
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```
FLASK_APP=websites/app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
API_TOKEN=your_cricket_api_token
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Project Structure

```
cricwizards/
├── websites/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   ├── app.py
│   └── models.py
├── src/
│   ├── cricket_api.py
│   └── get_team_performances.py
├── requirements.txt
└── README.md
```

## Usage

1. Register a new account or login
2. Select a team from the home page
3. View team performance analysis
4. Compare players
5. View predicted best XI
6. Explore player profiles

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Acknowledgments

- Cricket API (SportMonks) for providing cricket data
- Bootstrap for the frontend framework
- Flask for the web framework

## Contact

For any queries or support, please contact ozair0014@gmail.com 