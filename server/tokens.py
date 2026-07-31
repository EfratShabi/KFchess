import hashlib
import hmac
import os
import time

TOKEN_SECRET = os.environ.get('TOKEN_SECRET', 'dev-secret-change-me')
TOKEN_TTL_SECONDS = 3600


def _sign(payload):
    return hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


def create_token(username):
    expiry = int(time.time()) + TOKEN_TTL_SECONDS
    payload = f'{username}:{expiry}'
    return f'{payload}:{_sign(payload)}'


def verify_token(token):
    try:
        username, expiry_str, signature = token.rsplit(':', 2)
        expiry = int(expiry_str)
    except ValueError:
        return None
    payload = f'{username}:{expiry_str}'
    if not hmac.compare_digest(signature, _sign(payload)):
        return None
    if expiry < time.time():
        return None
    return username
