import os
import sqlite3
from datetime import datetime, timedelta

# Set project root and database path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, 'backend', 'demo_db.sqlite')

# Remove existing database if it exists
if os.path.exists(db_path):
    os.remove(db_path)

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT,
    last_name TEXT,
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
# ...existing code for other tables and sample data...

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Demo SQLite database created at: {db_path}")
