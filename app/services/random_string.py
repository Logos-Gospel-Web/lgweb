import random
import string

_valid_characters = string.ascii_letters + string.digits

def random_string():
    return ''.join(random.choices(_valid_characters, k=20))
