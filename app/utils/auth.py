"""Utility module for authentication helpers."""
import secrets
from datetime import datetime, timedelta
from flask import current_app, url_for
from flask_mail import Message
from app import db, mail
from app.models import MagicLink, User


class AuthHelper:
    """Helper functions for passwordless authentication."""
    
    @staticmethod
    def generate_magic_link(email):
        """
        Generate a magic link token for the given email.
        
        Args:
            email: User's email address
        
        Returns:
            str: The generated token
        """
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        
        # Store the token in the database
        magic_link = MagicLink(email=email, token=token)
        db.session.add(magic_link)
        db.session.commit()
        
        return token
    
    @staticmethod
    def send_magic_link(email, token):
        """
        Send a magic link email to the user.
        
        Args:
            email: User's email address
            token: Magic link token
        
        Returns:
            bool: True if email was sent successfully
        """
        try:
            # Generate the magic link URL
            magic_url = url_for('auth.verify_magic_link', token=token, _external=True)
            
            # Create email message
            msg = Message(
                'Your Login Link - Workout Tracker',
                recipients=[email]
            )
            msg.body = f"""
Hello!

Click the link below to log in to your Workout Tracker account:

{magic_url}

This link will expire in 1 hour.

If you didn't request this link, you can safely ignore this email.

Best regards,
Workout Tracker Team
"""
            msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ 
            display: inline-block; 
            padding: 12px 24px; 
            background-color: #007bff; 
            color: white; 
            text-decoration: none; 
            border-radius: 4px; 
            margin: 20px 0;
        }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Login to Workout Tracker</h2>
        <p>Click the button below to log in to your account:</p>
        <a href="{magic_url}" class="button">Log In</a>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #007bff;">{magic_url}</p>
        <div class="footer">
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this link, you can safely ignore this email.</p>
        </div>
    </div>
</body>
</html>
"""
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    @staticmethod
    def verify_token(token):
        """
        Verify a magic link token and return the associated email.
        
        Args:
            token: Magic link token to verify
        
        Returns:
            str or None: Email address if valid, None otherwise
        """
        magic_link = MagicLink.query.filter_by(token=token, used=False).first()
        
        if not magic_link:
            return None
        
        # Check if token has expired
        expiration = current_app.config['MAGIC_LINK_EXPIRATION']
        if datetime.utcnow() - magic_link.created_at > expiration:
            return None
        
        # Mark token as used
        magic_link.used = True
        db.session.commit()
        
        return magic_link.email
    
    @staticmethod
    def get_or_create_user(email, name=None):
        """
        Get existing user or create a new one.
        
        Args:
            email: User's email address
            name: User's name (optional, uses email prefix if not provided)
        
        Returns:
            User: The user object
        """
        user = User.query.filter_by(email=email).first()
        
        if not user:
            if name is None:
                # Use email prefix as name
                name = email.split('@')[0].title()
            
            user = User(email=email, name=name)
            db.session.add(user)
            db.session.commit()
        
        return user
