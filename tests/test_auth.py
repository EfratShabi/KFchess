from server.auth import hash_password, verify_password


def test_verify_accepts_correct_password():
    hash_hex, salt_hex = hash_password('correct-horse')
    assert verify_password('correct-horse', salt_hex, hash_hex) is True


def test_verify_rejects_wrong_password():
    hash_hex, salt_hex = hash_password('correct-horse')
    assert verify_password('wrong-password', salt_hex, hash_hex) is False


def test_same_password_gets_different_hash_each_time():
    hash_a, salt_a = hash_password('same-password')
    hash_b, salt_b = hash_password('same-password')
    assert salt_a != salt_b
    assert hash_a != hash_b


def test_hash_password_is_deterministic_given_same_salt():
    hash_a, salt = hash_password('same-password')
    hash_b, _ = hash_password('same-password', salt)
    assert hash_a == hash_b
