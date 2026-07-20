# backend/app/core/database.py
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any, List
from .config import config

class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self) -> None:
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                use_pure=True
            )
            print("✅ Database connected successfully!")
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            self.connection = None
    
    def get_cursor(self, dictionary: bool = True):
        """Get database cursor"""
        if not self.connection:
            self.connect()
        return self.connection.cursor(dictionary=dictionary)
    
    def execute(self, query: str, params: tuple = None):
        """Execute query and commit"""
        cursor = self.get_cursor()
        cursor.execute(query, params or ())
        self.connection.commit()
        return cursor
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        cursor = self.get_cursor()
        cursor.execute(query, params or ())
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        cursor = self.get_cursor()
        cursor.execute(query, params or ())
        return cursor.fetchall()
    
    def close(self) -> None:
        """Close connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

# Create a single instance (Singleton pattern)
db = Database()