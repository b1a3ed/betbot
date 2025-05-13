import sqlite3
import datetime
from pathlib import Path

coefficient = 2

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
            condition TEXT,
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
    if (user_betting == user_betting_on):
        return False
    else:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        success = False
        if (update_balance(user_betting, amount, False, c)):
            c.execute('INSERT INTO bets (user_id, coins_set, condition, target, timestamp, resolved, outcome) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                                        (str(user_betting), amount, condition, user_betting_on, datetime.datetime.now().isoformat(), 0, 0))
            print(f"User {user_betting} placed bet of {amount} on {condition} targeting {user_betting_on}.")
            success = True
        conn.commit()
        conn.close()
    return success

def update_balance(user_id, amount_delta, increase, c=None):
    if c is None:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            if increase:
                c.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (amount_delta, str(user_id)))
                print(f'Balance of {user_id} was updated with +{amount_delta} coins.')
            else:
                if(get_balance(user_id, c) >= amount_delta):
                    c.execute('UPDATE users SET coins = coins - ? WHERE user_id = ?', (amount_delta, str(user_id)))
                else:
                    print(f"User {user_id} has insufficient amount of coins for the bet.")
                    return False
            conn.commit()
    else:
        if increase:
            c.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (amount_delta, str(user_id)))
            print(f'Balance of {user_id} was updated with +{amount_delta} coins.')
        else:
            if(get_balance(user_id, c) >= amount_delta):
                c.execute('UPDATE users SET coins = coins - ? WHERE user_id = ?', (amount_delta, str(user_id)))
            else:
                print(f"User {user_id} has insufficient amount of coins for the bet.")
                return False
    return True

def get_my_bets(user_id, c=None):
    if c is None:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT id, coins_set, condition, target, timestamp FROM bets WHERE user_id = ? AND resolved = 0', (str(user_id), ) )
            result = c.fetchall()
    else:
            c.execute('SELECT id, coins_set, condition, target, timestamp FROM bets WHERE user_id = ? AND resolved = 0', (str(user_id), ) )
            result = c.fetchall()
    print(f'Retrieved all unresolved bets by user {user_id}.')
    return result if result else False

def get_all_bets(c=None):
    if c is None:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT id, coins_set, condition, target, timestamp FROM bets WHERE resolved = 0')
            results = c.fetchall()
            success = (len(results) > 0)
    else:
            c.execute('SELECT id, coins_set, condition, target, timestamp FROM bets WHERE resolved = 0')
            results = c.fetchall()
            success = (len(results) > 0)
    if success:
        print('Retrieved all unresolved bets.')
        return results
    else:
        print('Retrieval of all bets failed.')
        return False

def bet_resolve(bet_id, outcome, c=None):
    outcome = int(outcome)
    if c is None:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT user_id, coins_set FROM bets WHERE id = ?", (bet_id,))
            result = c.fetchone()
            if not result:
                print(f"No bet found with ID {bet_id}")
                return False
            else:
                UNPACKED_userid, UNPACKED_coins = result
                if (outcome == 1):
                    update_balance(UNPACKED_userid, UNPACKED_coins * coefficient, 1, c)
            c.execute('UPDATE bets SET resolved = 1, outcome = ? WHERE id = ?', (outcome, bet_id))
            conn.commit()
            success = (c.rowcount > 0)
    else:
            c.execute("SELECT user_id, coins_set FROM bets WHERE id = ?", (bet_id,))
            result = c.fetchone()
            if not result:
                print(f"No bet found with ID {bet_id}")
                return False
            else:
                UNPACKED_userid, UNPACKED_coins = result
                if outcome:
                    update_balance(UNPACKED_userid, UNPACKED_coins * coefficient, 1, c)
            c.execute('UPDATE bets SET resolved = 1, outcome = ? WHERE id = ?', (outcome, bet_id))
            success = (c.rowcount > 0)
    if success:
        print(f"Bet {bet_id} was resolved successfully")
    else:
        print(f"Bet {bet_id} could not be resolved.")
    return success

def resolve_target(target, outcome, c=None):
    outcome = int(outcome)
    resolved_bets = 0
    if c is None:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM bets WHERE target = ? AND resolved = 0", (target,))
            results = c.fetchall()
            bet_ids = [result[0] for result in results]
            for bet_id in bet_ids:
                bet_resolve(bet_id, outcome, c)
                resolved_bets+=1
            conn.commit()
    else:
        c.execute("SELECT id FROM bets WHERE target = ? AND resolved = 0", (target,))
        results = c.fetchall()
        bet_ids = [result[0] for result in results]
        for bet_id in bet_ids:
            bet_resolve(bet_id, outcome, c)
            resolved_bets+=1
        conn.commit()
    if resolved_bets:
        print(f"All bets for {target} were successfully resolved.")
        return True
    else:
        print(f"There was an error resolving all bets for {target}.")
        return False