from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """
    Function for generating hashed password
    :param password: user password
    :return: hashed password
    """
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Function for verifying hashed password
    :param plain_password: not hash password
    :param hashed_password: user hash password
    :return: bool
    """
    return password_hash.verify(plain_password, hashed_password)
