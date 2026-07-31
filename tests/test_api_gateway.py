from fastapi.testclient import TestClient

from server.api_gateway import create_app
from server.db import AccountRepository
from server.tokens import verify_token


def make_client(db_conn):
    repo = AccountRepository(db_conn)
    return TestClient(create_app(repo))


def test_register_returns_valid_token(db_conn):
    client = make_client(db_conn)

    response = client.post('/register', json={'username': 'alice', 'password': 'secret'})

    assert response.status_code == 200
    assert verify_token(response.json()['token']) == 'alice'


def test_register_duplicate_username_fails(db_conn):
    client = make_client(db_conn)
    client.post('/register', json={'username': 'alice', 'password': 'secret'})

    response = client.post('/register', json={'username': 'alice', 'password': 'other'})

    assert response.status_code == 409


def test_login_with_correct_password_succeeds(db_conn):
    client = make_client(db_conn)
    client.post('/register', json={'username': 'alice', 'password': 'secret'})

    response = client.post('/login', json={'username': 'alice', 'password': 'secret'})

    assert response.status_code == 200
    assert verify_token(response.json()['token']) == 'alice'


def test_login_with_wrong_password_fails(db_conn):
    client = make_client(db_conn)
    client.post('/register', json={'username': 'alice', 'password': 'secret'})

    response = client.post('/login', json={'username': 'alice', 'password': 'wrong'})

    assert response.status_code == 401
