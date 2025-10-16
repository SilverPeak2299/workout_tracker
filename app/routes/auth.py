"""Authentication routes for password-based login."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import timedelta
from app.utils.auth import AuthHelper

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Display login page and handle login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') in ['true', 'on', '1', 'True']
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/login.html')
        
        # Authenticate user
        user = AuthHelper.authenticate_user(email, password)
        
        if user:
            # Store user ID in session
            session['user_id'] = user.id
            session['user_email'] = user.email
            
            # Set session to permanent if "remember me" is checked
            if remember:
                session.permanent = True
            
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Display registration page and handle new user creation."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')
        
        # Check if user already exists
        if AuthHelper.get_user_by_email(email):
            flash('An account with this email already exists. Please login instead.', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = AuthHelper.create_user(email, password, name)
        
        # Log the user in automatically
        session['user_id'] = user.id
        session['user_email'] = user.email
        session.permanent = True  # Remember by default for new users
        
        flash(f'Welcome, {user.name}! Your account has been created.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html')


@bp.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
