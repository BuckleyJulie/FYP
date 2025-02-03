import sqlite3

DB_PATH = "data/results.db"

def init_db():
    """Initialize the database with the necessary table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            script_type TEXT,
            user_response TEXT,
            ai_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_interaction(employee_name, script_type, user_response, ai_response):
    """Log user interactions with AI in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_interactions (employee_name, script_type, user_response, ai_response)
        VALUES (?, ?, ?, ?)
    ''', (employee_name, script_type, user_response, ai_response))
    conn.commit()
    conn.close()

def get_user_data(employee_name):
    """Retrieve all interactions of a specific employee."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM user_interactions WHERE employee_name = ? ORDER BY timestamp
    ''', (employee_name,))
    data = cursor.fetchall()
    conn.close()
    return data
