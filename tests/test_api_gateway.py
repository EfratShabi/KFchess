from fastapi.testclient import TestClient

from core.config.constants import WHITE_COLOR, BLACK_COLOR
from server.api_gateway import create_app
from server.db import AccountRepository
from server.tokens import create_token, verify_token


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


def test_history_requires_authentication(db_conn):
    client = make_client(db_conn)

    response = client.get('/history')

    assert response.status_code in (401, 403)


def test_history_rejects_invalid_token(db_conn):
    client = make_client(db_conn)

    response = client.get('/history', headers={'Authorization': 'Bearer not-a-real-token'})

    assert response.status_code == 401


def test_history_is_empty_for_new_user(db_conn):
    client = make_client(db_conn)
    register_response = client.post('/register', json={'username': 'alice', 'password': 'secret'})
    token = register_response.json()['token']

    response = client.get('/history', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json() == []


def test_history_reflects_saved_games_from_both_perspectives(db_conn):
    repo = AccountRepository(db_conn)
    repo.register('alice', 'secret')
    repo.register('bob', 'secret')
    repo.save_result('room1', 'alice', 'bob', WHITE_COLOR, 1216, 1184)
    client = TestClient(create_app(repo))

    alice_history = client.get(
        '/history', headers={'Authorization': f'Bearer {create_token("alice")}'}).json()
    bob_history = client.get(
        '/history', headers={'Authorization': f'Bearer {create_token("bob")}'}).json()

    assert len(alice_history) == 1
    assert alice_history[0]['room_id'] == 'room1'
    assert alice_history[0]['opponent'] == 'bob'
    assert alice_history[0]['color'] == WHITE_COLOR
    assert alice_history[0]['result'] == 'win'
    assert alice_history[0]['rating_after'] == 1216

    assert len(bob_history) == 1
    assert bob_history[0]['opponent'] == 'alice'
    assert bob_history[0]['color'] == BLACK_COLOR
    assert bob_history[0]['result'] == 'loss'
    assert bob_history[0]['rating_after'] == 1184
