import random
import string

def generate_random_password(length=12):
    """
    Generate a random password with specified length
    containing uppercase, lowercase letters and digits
    """
    # Define the character set
    characters = string.ascii_letters + string.digits
    
    # Generate random password
    password = ''.join(random.choice(characters) for _ in range(length))
    
    return password

def parse_user_token(user_token: str) -> tuple[int, str]:
    """
    Parse user token into user_id and token
    Args:
        user_token: String in format "user_id-token"
    Returns:
        tuple: (user_id: int, token: str)
    Raises:
        ValueError: If token format is invalid
    """
    try:
        user_id, token = user_token.split('-')
        user_id = int(user_id)  # Convert user_id to integer
        return user_id, token
    except (ValueError, TypeError):
        raise ValueError("Invalid user token format")
