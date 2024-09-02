import bcrypt
from passlib.hash import bcrypt


def hash_password(password: str):
    hashed_pass = (bcrypt.hash(password))
    return hashed_pass


def check_password(hashed_password, provided_password):
    verify_pass = (bcrypt.verify(provided_password, hashed_password))
    return verify_pass


