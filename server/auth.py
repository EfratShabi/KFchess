import hashlib
import secrets

ITERATIONS = 100_000

def hash_password(password, salt_hex=None):
    salt_hex = salt_hex or secrets.token_hex(16)
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, ITERATIONS)
    return digest.hex(), salt_hex


def verify_password(password, salt_hex, expected_hash_hex):
    computed_hash_hex, _ = hash_password(password, salt_hex)
    return secrets.compare_digest(computed_hash_hex, expected_hash_hex)
