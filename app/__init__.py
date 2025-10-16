"""Flask application factory and initialization."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()


def create_app(config_object='config.Config'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Register blueprints
    from app.routes import auth, workout, coach, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(workout.bp)
    app.register_blueprint(coach.bp)
    app.register_blueprint(main.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
