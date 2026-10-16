from fastapi.testclient import TestClient


def test_cors_responds_ok_for_allowed_origin(client: TestClient):
    response = client.options(
        "/tasks",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_cors_response_fail_for_blocked_origin(client: TestClient):
    response = client.options(
        "/tasks",
        headers={
            "Origin": "http://example-site.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
