import sqlite3
import random
import string
from utils import generate_random_password

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Create users table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            telegram_name TEXT DEFAULT (CAST(telegram_id AS TEXT)),
            token TEXT NOT NULL,
            contribution INTEGER DEFAULT 0,
            credit INTEGER DEFAULT 0,
            total_usage INTEGER DEFAULT 0,
            daily_usage INTEGER DEFAULT 0,
            is_banned BOOLEAN DEFAULT 0
        )
    ''')
    
    # Reset daily_usage to 0 for all users
    c.execute('UPDATE users SET daily_usage = 0')
    
    conn.commit()
    conn.close()

def create_or_update_user(telegram_id: int, telegram_name: str = None) -> str:
    """
    Create a new user or update existing user's telegram_name in the database
    Args:
        telegram_id: User's Telegram ID
        telegram_name: User's Telegram name (optional)
    Returns:
        str: User's token
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Check if user already exists
    c.execute('SELECT token FROM users WHERE telegram_id = ?', (telegram_id,))
    existing_user = c.fetchone()
    
    if existing_user:
        # Update telegram_name if provided
        if telegram_name:
            c.execute('''
                UPDATE users 
                SET telegram_name = ?
                WHERE telegram_id = ?
            ''', (telegram_name, telegram_id))
            conn.commit()
        token = existing_user[0]
    else:
        # Generate random token for new user
        token = generate_random_password()
        
        # Insert new user
        c.execute('''
            INSERT INTO users (telegram_id, telegram_name, token)
            VALUES (?, ?, ?)
        ''', (telegram_id, telegram_name or str(telegram_id), token))
        conn.commit()
    
    conn.close()
    return token

def refresh_user_token(telegram_id: int) -> str:
    """
    Refresh user's token in the database
    Args:
        telegram_id: User's Telegram ID
    Returns:
        str: New token, or None if user doesn't exist
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute('SELECT 1 FROM users WHERE telegram_id = ?', (telegram_id,))
    if not c.fetchone():
        conn.close()
        return None
        
    # Generate and update new token
    new_token = generate_random_password()
    c.execute('''
        UPDATE users 
        SET token = ?
        WHERE telegram_id = ?
    ''', (new_token, telegram_id))
    
    conn.commit()
    conn.close()
    return new_token

def increase_contribution(telegram_id: int, amount: int = 1) -> bool:
    """
    Increase user's contribution by specified amount (default 1)
    Args:
        telegram_id: User's Telegram ID
        amount: Amount to increase (default 1)
    Returns:
        bool: True if successful, False if user doesn't exist
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute('SELECT 1 FROM users WHERE telegram_id = ?', (telegram_id,))
    if not c.fetchone():
        conn.close()
        return False
        
    # Update contribution
    c.execute('''
        UPDATE users 
        SET contribution = contribution + ?
        WHERE telegram_id = ?
    ''', (amount, telegram_id))
    
    conn.commit()
    conn.close()
    return True

def increase_credit(telegram_id: int, amount: int = -1) -> bool:
    """
    Increase user's credit by specified amount (default -1)
    Args:
        telegram_id: User's Telegram ID
        amount: Amount to increase (default -1)
    Returns:
        bool: True if successful, False if user doesn't exist
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute('SELECT 1 FROM users WHERE telegram_id = ?', (telegram_id,))
    if not c.fetchone():
        conn.close()
        return False
        
    # Update credit
    c.execute('''
        UPDATE users 
        SET credit = credit + ?
        WHERE telegram_id = ?
    ''', (amount, telegram_id))
    
    conn.commit()
    conn.close()
    return True

def increase_total_usage(telegram_id: int, amount: int = 1) -> bool:
    """
    Increase user's total_usage by specified amount (default 1)
    Args:
        telegram_id: User's Telegram ID
        amount: Amount to increase (default 1)
    Returns:
        bool: True if successful, False if user doesn't exist
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute('SELECT 1 FROM users WHERE telegram_id = ?', (telegram_id,))
    if not c.fetchone():
        conn.close()
        return False
        
    # Update total_usage
    c.execute('''
        UPDATE users 
        SET total_usage = total_usage + ?
        WHERE telegram_id = ?
    ''', (amount, telegram_id))
    
    conn.commit()
    conn.close()
    return True

def increase_daily_usage(telegram_id: int, amount: int = 1) -> bool:
    """
    Increase user's daily_usage by specified amount (default 1)
    Args:
        telegram_id: User's Telegram ID
        amount: Amount to increase (default 1)
    Returns:
        bool: True if successful, False if user doesn't exist
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute('SELECT 1 FROM users WHERE telegram_id = ?', (telegram_id,))
    if not c.fetchone():
        conn.close()
        return False
        
    # Update daily_usage
    c.execute('''
        UPDATE users 
        SET daily_usage = daily_usage + ?
        WHERE telegram_id = ?
    ''', (amount, telegram_id))
    
    conn.commit()
    conn.close()
    return True

def set_user_ban_status(telegram_id: int, ban: bool = True) -> bool:
    """
    Set user's ban status
    Args:
        telegram_id: User's Telegram ID
        ban: True to ban user, False to unban (default True)
    Returns:
        bool: True if successful, False if user doesn't exist
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute('SELECT 1 FROM users WHERE telegram_id = ?', (telegram_id,))
    if not c.fetchone():
        conn.close()
        return False
        
    # Update ban status
    c.execute('''
        UPDATE users 
        SET is_banned = ?
        WHERE telegram_id = ?
    ''', (ban, telegram_id))
    
    conn.commit()
    conn.close()
    return True

def get_user_info(telegram_id: int) -> dict:
    """
    Get user information from database
    Args:
        telegram_id: User's Telegram ID
    Returns:
        dict: User information including all fields, or None if user doesn't exist
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Get user info
    c.execute('''
        SELECT telegram_id, telegram_name, token, contribution, 
               credit, total_usage, daily_usage, is_banned
        FROM users 
        WHERE telegram_id = ?
    ''', (telegram_id,))
    
    user = c.fetchone()
    conn.close()
    
    if not user:
        return None
        
    # Convert tuple to dictionary
    return {
        'telegram_id': user[0],
        'telegram_name': user[1],
        'token': user[2],
        'contribution': user[3],
        'credit': user[4],
        'total_usage': user[5],
        'daily_usage': user[6],
        'is_banned': bool(user[7])
    }
