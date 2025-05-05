import sys
import os

# Add your application directory to Python path
sys.path.insert(0, '/home/w1907173/public_html/fyp')

# Set environment variables if needed
os.environ['FLASK_ENV'] = 'production'

# Import your Flask app
from cricwizards.website.app import app as application 