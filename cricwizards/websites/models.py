from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
    PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    
    def set_password(self, password):
        if not self.validate_password(password):
            raise ValueError("Password does not meet requirements")
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def validate_username(cls, username):
        return bool(cls.USERNAME_REGEX.match(username))
    
    @classmethod
    def validate_password(cls, password):
        return bool(cls.PASSWORD_REGEX.match(password))
    
    @classmethod
    def validate_email(cls, email):
        # Basic email validation
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_regex.match(email)) 