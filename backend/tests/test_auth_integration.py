import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration()
def test_register_new_user_and_return_data_without_secrets(client: TestClient):

    test_email = "test@example.com"

    response = client.post(
        "/register",
        json={"email": test_email, "password": "test123"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["email"] == test_email
    assert isinstance(body["id"], int)

    # El response_model=UserRead debe filtrar todo lo demas
    assert "password" not in body
    assert "hashed_password" not in body


@pytest.mark.integration()
def test_register_reject_creation_with_registered_email(client: TestClient):
    data = {"email": "repeat@example.com", "password": "repeated"}

    first_valid_request = client.post("/register", json=data)
    assert first_valid_request.status_code == 200

    second_invalid_request = client.post("/register", json=data)
    assert second_invalid_request.status_code == 409


@pytest.mark.integration()
def test_token_creation_with_valid_credentials(
    client: TestClient, registered_user: dict[str, str]
):
    response = client.post(
        "/token",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200

    json_data = response.json()

    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"


@pytest.mark.integration()
def test_token_reject_with_invalid_password(
    client: TestClient, registered_user: dict[str, str]
):

    invalid_password = "invalid"

    response = client.post(
        "/token",
        data={"username": registered_user["email"], "password": invalid_password},
    )

    assert response.status_code == 401

    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.integration()
def test_token_reject_with_invalid_email(client: TestClient):
    email = "invalid@example.com"
    password = "test123"

    response = client.post("/token", data={"username": email, "password": password})

    assert response.status_code == 401


@pytest.mark.integration()
def test_get_current_user_rejects_with_no_token(client: TestClient):

    response = client.get("/users/me")

    assert response.status_code == 401


@pytest.mark.integration()
def test_get_current_user_rejects_with_invalid_token(client: TestClient):

    token = "bad-token"

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


@pytest.mark.integration()
def test_complete_auth_flow(client: TestClient):
    email = "test2@example.com"
    password = "test124"

    register_response = client.post(
        "/register", json={"email": email, "password": password}
    )

    assert register_response.status_code == 200

    token_response = client.post(
        "/token", data={"username": email, "password": password}
    )

    assert token_response.status_code == 200

    access_token = token_response.json()["access_token"]

    get_user_response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert get_user_response.status_code == 200

    user_response_json = get_user_response.json()

    assert isinstance(user_response_json["id"], int)
    assert user_response_json["email"] == email
