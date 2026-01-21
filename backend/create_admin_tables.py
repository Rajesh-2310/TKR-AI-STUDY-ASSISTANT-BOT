"""
Database migration script for admin authentication system
Creates tables for admin users, verification codes, and sessions
"""
import pymysql
from database import get_db

def create_admin_tables():
    """Create admin authentication tables"""
    db = get_db()
    
    # Create admin_users table
    admin_users_sql = """
    CREATE TABLE IF NOT EXISTS admin_users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        is_verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    
    # Create verification_codes table
    verification_codes_sql = """
    CREATE TABLE IF NOT EXISTS verification_codes (
        id INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) NOT NULL,
        code VARCHAR(6) NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        used BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_email (email),
        INDEX idx_code (code)
    )
    """
    
    # Create admin_sessions table
    admin_sessions_sql = """
    CREATE TABLE IF NOT EXISTS admin_sessions (
        id INT PRIMARY KEY AUTO_INCREMENT,
        admin_id INT NOT NULL,
        session_token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES admin_users(id) ON DELETE CASCADE,
        INDEX idx_token (session_token)
    )
    """
    
    try:
        print("Creating admin_users table...")
        db.execute_query(admin_users_sql, fetch=False)
        print("✓ admin_users table created")
        
        print("Creating verification_codes table...")
        db.execute_query(verification_codes_sql, fetch=False)
        print("✓ verification_codes table created")
        
        print("Creating admin_sessions table...")
        db.execute_query(admin_sessions_sql, fetch=False)
        print("✓ admin_sessions table created")
        
        print("\n✅ All admin authentication tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_admin_tables()
