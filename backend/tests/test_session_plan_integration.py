import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_plan_sessions_returns_valid_pomodoro_plan(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")

    input = {
        "mode": "classic",
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    plan_session_response = client.post("/sessions/plan", json=input, headers=john)

    assert plan_session_response.status_code == 200

    plan = plan_session_response.json()

    assert plan["work_times"] == [25, 25, 25, 25]
    assert plan["break_times"] == [5, 5, 5]


@pytest.mark.integration
def test_plan_sessions_fails_without_user_credential(client: TestClient):

    input = {
        "mode": "classic",
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    plan_session_response = client.post("/sessions/plan", json=input)

    assert plan_session_response.status_code == 401


@pytest.mark.integration
def test_plan_sessions_fails_if_request_includes_broken_constraints(
    client: TestClient, auth_headers
):

    john = auth_headers("john@example.com")

    input = {
        "mode": "incremental",
        "start_minutes": 20,
        "cap_minutes": 10,  # cap_minutes debe ser >= start_minutes
        "growth": 2,
        "num_of_rounds": 4,
    }

    plan_session_response = client.post("/sessions/plan", json=input, headers=john)

    assert plan_session_response.status_code == 422

    response_body = plan_session_response.json()

    detail = response_body["detail"][0]

    assert detail["type"] == "pomodoro_validation_error"
    assert detail["loc"] == ["body", "cap_minutes"]


@pytest.mark.integration
def test_plan_sessions_fails_with_an_unknown_mode(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")

    input = {
        "mode": "test",  # Modo invalido
        "start_minutes": 20,
        "num_of_rounds": 4,
    }

    plan_session_response = client.post("/sessions/plan", json=input, headers=john)

    assert plan_session_response.status_code == 422

    detail = plan_session_response.json()["detail"][0]

    assert detail["type"] == "union_tag_invalid"
    assert detail["loc"] == ["body"]
