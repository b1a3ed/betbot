import sqlite3
from pathlib import Path

DB_FILE = Path("data/users.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        coins INTEGER DEFAULT 1000
    )''')
    conn.commit()
    conn.close()
    print(f'DB initialized')

def add_user_if_not_exists(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (str(user_id),))
    conn.commit()
    conn.close()
    print(f"Added user {user_id}")

def add_coins(user_id, amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (amount, str(user_id)))
    conn.commit()
    conn.close()
    print(f'Added {amount} coins to user {user_id}. Current balance of {user_id} is {get_balance(user_id)}')

def get_balance(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f'SELECT coins FROM users WHERE user_id = ?', (str(user_id),))
    result = c.fetchone()
    conn.close()
    print(f'Retrieved amount of coins of {user_id}')
    return result[0] if result else 0

    