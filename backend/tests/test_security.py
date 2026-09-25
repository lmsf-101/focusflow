from focusflow_api.security import hash_password, verify_password


def test_hash_password_is_different_from_plain_password():
    password = "test123"
    hashed_password = hash_password(password)

    assert hashed_password != password


def test_hash_password_salt_where_same_password_returns_different_results():
    result1 = hash_password("test123")
    result2 = hash_password("test123")

    assert result1 != result2


def test_verify_password_returns_true_with_same_password():
    password_test = "correct"

    hashed_password = hash_password(password_test)

    assert verify_password(password_test, hashed_password) is True


def test_verify_password_returns_false_with_different_password():
    password_test = "correct"
    password_incorrect = "incorrect"

    hashed_password = hash_password(password_test)

    assert verify_password(password_incorrect, hashed_password) is False
