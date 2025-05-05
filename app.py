#!/usr/bin/env python3
from flask import Flask, render_template, url_for
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/performance')
def performance():
    return render_template('performance.html')

if __name__ == '__main__':
    app.run(debug=True) 