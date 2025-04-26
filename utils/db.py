import sqlite3
import datetime
from pathlib import Path

DB_FILE = Path("data/users.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            coins INTEGER DEFAULT 1000
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            coins_set INTEGER,
            condition BOOLEAN,
            target TEXT,
            timestamp TEXT,
            resolved BOOLEAN DEFAULT 0,
            outcome BOOLEAN      
              )''')
    conn.commit()
    conn.close()
    print(f'DB initialized')

def add_user_if_not_exists(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (str(user_id),))
    conn.commit()
    if (c.rowcount > 0):
        print(f"Added user {user_id}")    
    conn.close()

def add_coins(user_id, amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (amount, str(user_id)))
    conn.commit()
    conn.close()
    print(f'Added {amount} coins to user {user_id}. Current balance of {user_id} is {get_balance(user_id)}')

def get_balance(user_id, c=None):
    if c is None:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f'SELECT coins FROM users WHERE user_id = ?', (str(user_id),))
        result = c.fetchone()
        conn.close()
    else:
        c.execute(f'SELECT coins FROM users WHERE user_id = ?', (str(user_id),))
        result = c.fetchone()
    print(f'Retrieved amount of coins of {user_id}.')
    return result[0] if result else 0

def insert_bet(amount, condition, user_betting, user_betting_on):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    success = False
    if (update_balance(user_betting, amount, False)):
        c.execute('INSERT INTO bets (user_id, coins_set, condition, target, timestamp, resolved, outcome) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                                    (str(user_betting), amount, condition, user_betting_on, datetime.datetime.now().isoformat(), 0, 0))
        print(f"User {user_betting} placed bet of {amount} on {condition} targeting {user_betting_on}.")
        success = True
    conn.commit()
    conn.close()
    return success

def update_balance(user_id, amount_delta, increase):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if increase:
            c.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (amount_delta, str(user_id)))
        else:
            if(get_balance(user_id, c) >= amount_delta):
                c.execute('UPDATE users SET coins = coins - ? WHERE user_id = ?', (amount_delta, str(user_id)))
            else:
                print(f"User {user_id} has insufficient amount of coins for the bet.")
                return False
        conn.commit()
        print(f"User {user_id} has successfully placed a bet of {amount_delta} coins.")
        return True
