"""Database models for the workout tracker application."""
from datetime import datetime
from app import db
import secrets


class User(db.Model):
    """User model for storing user information."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Share token for coach view
    share_token = db.Column(db.String(32), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(24))
    
    # Relationships
    workout_logs = db.relationship('WorkoutLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'


class WorkoutLog(db.Model):
    """Model for logging complete workouts."""
    
    __tablename__ = 'workout_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    workout_name = db.Column(db.String(100), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)  # Week in cycle (1-4 for 3+1)
    split = db.Column(db.String(1), nullable=False)  # 'A' or 'B'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sets = db.relationship('SetLog', backref='workout', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<WorkoutLog {self.workout_name} - {self.date}>'


class SetLog(db.Model):
    """Model for logging individual sets."""
    
    __tablename__ = 'set_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    workout_log_id = db.Column(db.Integer, db.ForeignKey('workout_logs.id'), nullable=False, index=True)
    exercise_name = db.Column(db.String(100), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    rpe = db.Column(db.Float)  # Rate of Perceived Exertion (1-10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SetLog {self.exercise_name} - Set {self.set_number}>'


class MagicLink(db.Model):
    """Model for storing magic link tokens for passwordless authentication."""
    
    __tablename__ = 'magic_links'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<MagicLink {self.email}>'
