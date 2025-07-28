import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    # ✅ This is the fix: added missing parenthesis and allows dynamic profile pictures
    profile_pic = db.Column(db.String(100), default='default-avatar.png')

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    loan = db.Column(db.Float, default=0.0)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///micro_lending.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
