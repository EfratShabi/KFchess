import server.auth.tokens as tokens
from server.auth.tokens import create_token, verify_token


def test_valid_token_returns_username():
    token = create_token('alice')
    assert verify_token(token) == 'alice'


def test_tampered_token_is_rejected():
    token = create_token('alice')
    tampered = token[:-1] + ('0' if token[-1] != '0' else '1')
    assert verify_token(tampered) is None


def test_expired_token_is_rejected(monkeypatch):
    monkeypatch.setattr(tokens, 'TOKEN_TTL_SECONDS', -1)
    token = tokens.create_token('alice')
    assert tokens.verify_token(token) is None


def test_malformed_token_is_rejected():
    assert verify_token('not-a-valid-token') is None


def test_missing_token_is_rejected():
    assert verify_token(None) is None


def test_token_for_different_username_has_different_signature():
    assert create_token('alice') != create_token('bob')
