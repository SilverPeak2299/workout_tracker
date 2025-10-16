"""Configuration module for the Flask application."""
import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///workout_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration - remember users for 3 days
    PERMANENT_SESSION_LIFETIME = timedelta(days=3)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ['true', 'on', '1']
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Program JSON file path
    PROGRAM_JSON_PATH = os.environ.get('PROGRAM_JSON_PATH') or 'program.json'
