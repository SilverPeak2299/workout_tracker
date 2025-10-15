"""Main application routes."""
from flask import Blueprint, render_template, session, redirect, url_for
from app.models import User

bp = Blueprint('main', __name__)


def login_required(f):
    """Decorator to require login for routes."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    
    return decorated_function


@bp.route('/')
def index():
    """Home page - redirects to login or dashboard."""
    if 'user_id' in session:
        return redirect(url_for('workout.dashboard'))
    return redirect(url_for('auth.login'))
