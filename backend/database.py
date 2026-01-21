import pymysql
from pymysql.cursors import DictCursor
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database connection and query utilities"""
    
    def __init__(self):
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                cursorclass=DictCursor,
                autocommit=False
            )
            logger.info("Database connection established")
            return self.connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
                    return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_many(self, query, params_list):
        """Execute multiple queries with different parameters"""
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(query, params_list)
                self.connection.commit()
                return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Batch execution failed: {e}")
            raise

# Global database instance
db = Database()

def get_db():
    """Get database connection"""
    if not db.connection or not db.connection.open:
        db.connect()
    return db

def init_db():
    """Initialize database with schema"""
    try:
        connection = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        
        with connection.cursor() as cursor:
            # Read and execute schema file
            with open('../database/schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
                # Split by semicolon and execute each statement
                statements = [s.strip() for s in schema.split(';') if s.strip()]
                for statement in statements:
                    cursor.execute(statement)
        
        connection.commit()
        connection.close()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
