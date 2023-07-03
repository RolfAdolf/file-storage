import hashlib
import random
from datetime import datetime


def file_hash(username: str, file_bytes: bytes) -> str:
    """
    Calculate the hash using user, file, and time information.
    """
    h = hashlib.sha256()
    h.update(username.encode())
    h.update(file_bytes)
    current_time = str(datetime.now()).encode()
    h.update(current_time)
    return h.hexdigest()


def generate_random_string():
    random_number = str(random.random()).encode()
    current_time = str(datetime.now()).encode()

    h = hashlib.sha256()
    h.update(random_number)
    h.update(current_time)

    return h.hexdigest()
