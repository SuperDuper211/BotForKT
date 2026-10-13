import sqlite3

def init_db():
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood TEXT,
            work REAL,
            sleep REAL,
            comment TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_log(user_id, mood, work, sleep, comment, date):
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO logs (user_id, mood, work, sleep, comment, date) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, mood, work, sleep, comment, date))
    conn.commit()
    conn.close()

def get_user_logs(user_id):
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT mood, work, sleep, comment, date FROM logs WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_all(user_id):
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM logs WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()