"""
Database Schema
Tables:
- videos: YouTube video metadata
- subtitles: Raw subtitle content
- vocabulary: Extracted German words with CEFR levels
- flashcards: Generated example sentences
- user_progress: User learning statistics
"""

import sqlite3
import os

DB_PATH = 'data/linguacopilot.db'


def create_database():
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        published_at TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT UNIQUE NOT NULL,
        level TEXT NOT NULL,
        count INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        level TEXT NOT NULL,
        sentence_de TEXT NOT NULL,
        sentence_fr TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (word) REFERENCES vocabulary(word)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        correct_count INTEGER DEFAULT 0,
        incorrect_count INTEGER DEFAULT 0,
        last_seen TIMESTAMP,
        FOREIGN KEY (word) REFERENCES vocabulary(word)
    )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created at {DB_PATH}")


if __name__ == '__main__':
    create_database()

