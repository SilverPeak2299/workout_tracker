"""Utility module for authentication helpers."""
from app import db
from app.models import User


class AuthHelper:
    """Helper functions for password-based authentication."""
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email address
            password: User's password
        
        Returns:
            User or None: The user object if authentication is successful, None otherwise
        """
        user = User.query.filter_by(email=email.strip().lower()).first()
        
        if user and user.check_password(password):
            return user
        
        return None
    
    @staticmethod
    def create_user(email, password, name=None):
        """
        Create a new user.
        
        Args:
            email: User's email address
            password: User's password
            name: User's name (optional, uses email prefix if not provided)
        
        Returns:
            User: The newly created user object
        """
        if name is None:
            # Use email prefix as name
            name = email.split('@')[0].title()
        
        user = User(email=email.strip().lower(), name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def get_user_by_email(email):
        """
        Get a user by email address.
        
        Args:
            email: User's email address
        
        Returns:
            User or None: The user object if found, None otherwise
        """
        return User.query.filter_by(email=email.strip().lower()).first()
