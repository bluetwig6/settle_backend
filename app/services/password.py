from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def get_password_hash(password:str) -> str:
    return password_hash.hash(password)

def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    print('****', plain_password, hashed_password)
    """
    Check if the user password from request is valid.
    """
    return password_hash.verify(plain_password, hashed_password)
