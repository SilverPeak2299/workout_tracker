"""Authentication routes for passwordless login."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth import AuthHelper

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Display login page and handle magic link generation."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('auth/login.html')
        
        # Generate and send magic link
        token = AuthHelper.generate_magic_link(email)
        
        # In development mode without mail server, show the link
        if not AuthHelper.send_magic_link(email, token):
            # Mail sending failed, show debug link
            magic_url = url_for('auth.verify_magic_link', token=token, _external=True)
            flash(
                f'Email service not configured. Use this link to log in: {magic_url}',
                'warning'
            )
        else:
            flash(
                f'A login link has been sent to {email}. Please check your inbox.',
                'success'
            )
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')


@bp.route('/verify/<token>')
def verify_magic_link(token):
    """Verify magic link token and log user in."""
    email = AuthHelper.verify_token(token)
    
    if not email:
        flash('Invalid or expired login link. Please request a new one.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get or create user
    user = AuthHelper.get_or_create_user(email)
    
    # Store user ID in session
    session['user_id'] = user.id
    session['user_email'] = user.email
    
    flash(f'Welcome back, {user.name}!', 'success')
    return redirect(url_for('main.index'))


@bp.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
