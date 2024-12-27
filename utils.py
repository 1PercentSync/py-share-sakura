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