import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "configs", "sqlite.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()

def get_user_data():
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM user_data")
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}

def save_user_data(data: dict):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for k, v in data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO user_data (key, value)
                VALUES (?, ?)
            """, (k, str(v)))
        conn.commit()
