"""Configuration module for the Flask application."""
import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///workout_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Magic link token expiration (1 hour)
    MAGIC_LINK_EXPIRATION = timedelta(hours=1)
    
    # Mail configuration for magic links
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Program JSON file path
    PROGRAM_JSON_PATH = os.environ.get('PROGRAM_JSON_PATH') or 'program.json'
