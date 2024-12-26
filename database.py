import sqlite3

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            contribution INTEGER DEFAULT 0,
            credit INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def is_token_valid(token: str) -> bool:
    """Check if token exists in database"""
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    result = c.fetchone()
    conn.close()
    return result is not None

def add_or_update_token(token: str, contribution: int = 0, credit: int = 0):
    """Add or update token information"""
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO tokens (token, contribution, credit) 
        VALUES (?, ?, ?)
    ''', (token, contribution, credit))
    conn.commit()
    conn.close()

def get_token_info(token: str):
    """Get token information"""
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('SELECT token, contribution, credit FROM tokens WHERE token = ?', (token,))
    result = c.fetchone()
    conn.close()
    return result 