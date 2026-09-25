from pwdlib import PasswordHash

pass_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return pass_hash.hash(password)


def verify_password(text: str, hash_password: str) -> bool:
    return pass_hash.verify(text, hash_password)
