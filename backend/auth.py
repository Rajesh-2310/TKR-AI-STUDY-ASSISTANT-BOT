"""
Authentication utilities for admin system
Handles password hashing, session management, and email verification
"""
import bcrypt
import secrets
import random
from datetime import datetime, timedelta
from database import get_db
import logging

logger = logging.getLogger(__name__)

# Allowed admin email
ALLOWED_ADMIN_EMAIL = "raj123esh456nani99@gmail.com"

class AuthService:
    """Authentication service for admin users"""
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def generate_session_token():
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_verification_code():
        """Generate a 6-digit verification code"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def is_email_allowed(email):
        """Check if email is allowed to register as admin"""
        return email.lower() == ALLOWED_ADMIN_EMAIL.lower()
    
    @staticmethod
    def create_admin_user(email, password):
        """Create a new admin user"""
        try:
            if not AuthService.is_email_allowed(email):
                return {'success': False, 'error': 'Email not authorized for admin access'}
            
            db = get_db()
            
            # Check if user already exists
            existing = db.execute_query(
                "SELECT id FROM admin_users WHERE email = %s",
                (email,)
            )
            
            if existing:
                return {'success': False, 'error': 'Admin user already exists'}
            
            # Hash password
            password_hash = AuthService.hash_password(password)
            
            # Create user
            db.execute_query(
                "INSERT INTO admin_users (email, password_hash, is_verified) VALUES (%s, %s, %s)",
                (email, password_hash, False),
                fetch=False
            )
            
            logger.info(f"Admin user created: {email}")
            return {'success': True, 'message': 'Admin user created successfully'}
            
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def create_verification_code(email):
        """Create and store a verification code"""
        try:
            db = get_db()
            
            # Generate code
            code = AuthService.generate_verification_code()
            
            # Set expiration (10 minutes from now)
            expires_at = datetime.now() + timedelta(minutes=10)
            
            # Store code
            db.execute_query(
                "INSERT INTO verification_codes (email, code, expires_at) VALUES (%s, %s, %s)",
                (email, code, expires_at),
                fetch=False
            )
            
            logger.info(f"Verification code created for {email}")
            return {'success': True, 'code': code}
            
        except Exception as e:
            logger.error(f"Error creating verification code: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def verify_code(email, code):
        """Verify a verification code"""
        try:
            db = get_db()
            
            # Get the most recent unused code for this email
            result = db.execute_query(
                """SELECT id, expires_at FROM verification_codes 
                   WHERE email = %s AND code = %s AND used = FALSE 
                   ORDER BY created_at DESC LIMIT 1""",
                (email, code)
            )
            
            if not result:
                return {'success': False, 'error': 'Invalid verification code'}
            
            code_data = result[0]
            
            # Check if expired
            if datetime.now() > code_data['expires_at']:
                return {'success': False, 'error': 'Verification code expired'}
            
            # Mark code as used
            db.execute_query(
                "UPDATE verification_codes SET used = TRUE WHERE id = %s",
                (code_data['id'],),
                fetch=False
            )
            
            # Mark user as verified
            db.execute_query(
                "UPDATE admin_users SET is_verified = TRUE WHERE email = %s",
                (email,),
                fetch=False
            )
            
            logger.info(f"Email verified for {email}")
            return {'success': True, 'message': 'Email verified successfully'}
            
        except Exception as e:
            logger.error(f"Error verifying code: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def login(email, password):
        """Login admin user"""
        try:
            db = get_db()
            
            # Get user
            user = db.execute_query(
                "SELECT id, password_hash, is_verified FROM admin_users WHERE email = %s",
                (email,)
            )
            
            if not user:
                return {'success': False, 'error': 'Invalid email or password'}
            
            user_data = user[0]
            
            # Check if verified
            if not user_data['is_verified']:
                return {'success': False, 'error': 'Email not verified. Please verify your email first.'}
            
            # Verify password
            if not AuthService.verify_password(password, user_data['password_hash']):
                return {'success': False, 'error': 'Invalid email or password'}
            
            # Create session
            session_token = AuthService.generate_session_token()
            expires_at = datetime.now() + timedelta(days=7)  # 7 days session
            
            db.execute_query(
                "INSERT INTO admin_sessions (admin_id, session_token, expires_at) VALUES (%s, %s, %s)",
                (user_data['id'], session_token, expires_at),
                fetch=False
            )
            
            logger.info(f"Admin logged in: {email}")
            return {
                'success': True,
                'session_token': session_token,
                'email': email
            }
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def verify_session(session_token):
        """Verify a session token"""
        try:
            db = get_db()
            
            # Get session
            result = db.execute_query(
                """SELECT s.admin_id, s.expires_at, u.email 
                   FROM admin_sessions s
                   JOIN admin_users u ON s.admin_id = u.id
                   WHERE s.session_token = %s""",
                (session_token,)
            )
            
            if not result:
                return {'success': False, 'error': 'Invalid session'}
            
            session_data = result[0]
            
            # Check if expired
            if datetime.now() > session_data['expires_at']:
                return {'success': False, 'error': 'Session expired'}
            
            return {
                'success': True,
                'admin_id': session_data['admin_id'],
                'email': session_data['email']
            }
            
        except Exception as e:
            logger.error(f"Error verifying session: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def logout(session_token):
        """Logout admin user"""
        try:
            db = get_db()
            
            db.execute_query(
                "DELETE FROM admin_sessions WHERE session_token = %s",
                (session_token,),
                fetch=False
            )
            
            logger.info("Admin logged out")
            return {'success': True, 'message': 'Logged out successfully'}
            
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return {'success': False, 'error': str(e)}
