import sqlite3
from utils import generate_random_password
import asyncio
import time

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Create users table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            telegram_name TEXT NOT NULL,
            token TEXT NOT NULL,
            contribution INTEGER DEFAULT 0,
            credit INTEGER DEFAULT 0,
            total_usage INTEGER DEFAULT 0,
            daily_usage INTEGER DEFAULT 0,
            is_banned BOOLEAN DEFAULT 0,
            temp_ban_until INTEGER DEFAULT 0
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
        
        # Insert new user with temp_ban_until = 0
        c.execute('''
            INSERT INTO users (telegram_id, telegram_name, token, temp_ban_until)
            VALUES (?, ?, ?, 0)
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
    Credit will not go below 0
    Args:
        telegram_id: User's Telegram ID
        amount: Amount to increase (default -1)
    Returns:
        bool: True if successful, False if user doesn't exist
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Check if user exists and get current credit
    c.execute('SELECT credit FROM users WHERE telegram_id = ?', (telegram_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return False
    
    current_credit = result[0]
    # Calculate new credit, ensure it doesn't go below 0
    new_credit = max(0, current_credit + amount)
        
    # Update credit
    c.execute('''
        UPDATE users 
        SET credit = ?
        WHERE telegram_id = ?
    ''', (new_credit, telegram_id))
    
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

#Unused
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

def get_top_contributors(limit: int = 5) -> list:
    """
    Get top N users with highest contribution (>0)
    Args:
        limit: Number of users to return (default 5)
    Returns:
        list: List of tuples (telegram_name, contribution)
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT telegram_name, contribution
        FROM users
        WHERE contribution > 0
        ORDER BY contribution DESC
        LIMIT ?
    ''', (limit,))
    
    result = c.fetchall()
    conn.close()
    return result

def get_top_credits(limit: int = 5) -> list:
    """
    Get top N users with highest credit (>0)
    Args:
        limit: Number of users to return (default 5)
    Returns:
        list: List of tuples (telegram_name, credit)
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT telegram_name, credit
        FROM users
        WHERE credit > 0
        ORDER BY credit DESC
        LIMIT ?
    ''', (limit,))
    
    result = c.fetchall()
    conn.close()
    return result

def get_top_total_usage(limit: int = 5) -> list:
    """
    Get top N users with highest total usage (>0)
    Args:
        limit: Number of users to return (default 5)
    Returns:
        list: List of tuples (telegram_name, total_usage)
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT telegram_name, total_usage
        FROM users
        WHERE total_usage > 0
        ORDER BY total_usage DESC
        LIMIT ?
    ''', (limit,))
    
    result = c.fetchall()
    conn.close()
    return result

def get_top_daily_usage(limit: int = 5) -> list:
    """
    Get top N users with highest daily usage (>0)
    Args:
        limit: Number of users to return (default 5)
    Returns:
        list: List of tuples (telegram_name, daily_usage)
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT telegram_name, daily_usage
        FROM users
        WHERE daily_usage > 0
        ORDER BY daily_usage DESC
        LIMIT ?
    ''', (limit,))
    
    result = c.fetchall()
    conn.close()
    return result

#Unused
def is_temp_banned(telegram_id: int) -> bool:
    """
    Check if user is temporarily banned
    Args:
        telegram_id: User's Telegram ID
    Returns:
        bool: True if user is temp banned and ban period hasn't expired, False otherwise
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Get user's temp ban timestamp
    c.execute('''
        SELECT temp_ban_until 
        FROM users 
        WHERE telegram_id = ?
    ''', (telegram_id,))
    
    result = c.fetchone()
    conn.close()
    
    if not result:
        return False
    
    # Compare with current timestamp
    current_time = int(asyncio.get_event_loop().time())
    return result[0] > current_time

def set_temp_ban(telegram_id: int, ban_until: int) -> bool:
    """
    Set user's temporary ban end time
    Args:
        telegram_id: User's Telegram ID
        ban_until: Unix timestamp when ban should end (0 to remove temp ban)
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
        
    # Update temp ban timestamp
    c.execute('''
        UPDATE users 
        SET temp_ban_until = ?
        WHERE telegram_id = ?
    ''', (ban_until, telegram_id))
    
    conn.commit()
    conn.close()
    return True

def is_token_valid(telegram_id: int, token: str) -> bool:
    """
    Check if user's token is valid
    Args:
        telegram_id: User's Telegram ID
        token: Token to validate
    Returns:
        bool: True if token is valid, False otherwise
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Check if user exists and get token, ban status and temp ban timestamp
    c.execute('''
        SELECT token, is_banned, temp_ban_until
        FROM users 
        WHERE telegram_id = ?
    ''', (telegram_id,))
    
    result = c.fetchone()
    conn.close()
    
    # User doesn't exist
    if not result:
        return False
        
    stored_token, is_banned, temp_ban_until = result
    
    # Check permanent ban
    if is_banned:
        return False
        
    # Check temporary ban
    current_time = int(time.time())
    if temp_ban_until > current_time:
        return False
        
    # Check token match
    return token == stored_token

if __name__ == "__main__":
    init_db()