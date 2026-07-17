# backend/app/database.py
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 3306)),
                database=os.getenv('DB_NAME', 'stellarx'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'sandulna0727'),
                use_pure=True
            )
            print("✅ Database connected successfully!")
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            self.connection = None
    
    def get_cursor(self, dictionary=True):
        if not self.connection:
            self.connect()
        return self.connection.cursor(dictionary=dictionary)
    
    def execute(self, query, params=None):
        cursor = self.get_cursor()
        cursor.execute(query, params or ())
        self.connection.commit()
        return cursor
    
    def fetch_one(self, query, params=None):
        cursor = self.get_cursor()
        cursor.execute(query, params or ())
        return cursor.fetchone()
    
    def fetch_all(self, query, params=None):
        cursor = self.get_cursor()
        cursor.execute(query, params or ())
        return cursor.fetchall()
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

db = Database()