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
<<<<<<< HEAD
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_name TEXT NOT NULL,
        script_choice TEXT NOT NULL,
        interaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
=======
>>>>>>> d269442 (restart)
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

def get_summary_data():
<<<<<<< HEAD
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(DISTINCT employee_name) FROM interactions")
    total_employees = cursor.fetchone()[0]
    
    cursor.execute('''
    SELECT script_choice, COUNT(*) 
    FROM interactions 
    GROUP BY script_choice
    ''')
    training_needs = dict(cursor.fetchall())
    
    conn.close()
    return {
        'total_employees': total_employees,
        'training_needs': training_needs
    }
=======
    conn = sqlite3.connect("phishing.db")
    cursor = conn.cursor()
    
    # Get total employees tested
    cursor.execute("SELECT COUNT(DISTINCT employee_name) FROM interactions")
    total_employees = cursor.fetchone()[0]
    
    # Get training needs statistics
    cursor.execute("SELECT user_response FROM interactions")
    responses = cursor.fetchall()
    
    training_needs = {"Phishing Awareness": 0, "Data Sharing Risks": 0, "Email Verification": 0}
    
    for (response,) in responses:
        if "clicked" in response.lower() or "entered" in response.lower():
            training_needs["Phishing Awareness"] += 1
        if "shared" in response.lower() or "provided" in response.lower():
            training_needs["Data Sharing Risks"] += 1
        if "trusted" in response.lower() or "assumed" in response.lower():
            training_needs["Email Verification"] += 1
    
    conn.close()
    
    return {"total_employees": total_employees, "training_needs": training_needs}
>>>>>>> d269442 (restart)
