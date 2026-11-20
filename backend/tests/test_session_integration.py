import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_create_session_returns_planned_config_and_copied_tasks(
    client: TestClient, auth_headers, make_task, make_category
):
    john = auth_headers("john@example.com")
    john_task = make_task(john, title="Task A")
    john_category = make_category(john)

    john_task_with_category = make_task(
        john, title="Task B", category_id=john_category["id"]
    )

    params = {
        "mode": "classic",
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }
    session_tasks = [
        {"task_id": john_task["id"], "estimate_minutes": 25},
        {"task_id": john_task_with_category["id"]},
    ]

    session_input = {"params": params, "tasks": session_tasks}

    session_post_request = client.post("/sessions", json=session_input, headers=john)

    assert session_post_request.status_code == 201

    pomodoro_session = session_post_request.json()

    assert pomodoro_session["status"] == "active"
    assert pomodoro_session["mode"] == "classic"
    assert pomodoro_session["ended_at"] is None

    planned_config = pomodoro_session["planned_config"]

    assert planned_config["schema_version"] == 1
    assert planned_config["params"] == params

    assert planned_config["plan"]["work_times"] == [25, 25, 25, 25]
    assert planned_config["plan"]["break_times"] == [5, 5, 5]

    rows = {row["task_title"]: row for row in pomodoro_session["session_tasks"]}

    assert set(rows) == {"Task A", "Task B"}

    for task in rows.values():
        assert task["actual_minutes"] == 0
        assert task["completed"] is False

    task_a = rows["Task A"]
    assert task_a["task_id"] == john_task["id"]
    assert task_a["category_id"] is None
    assert task_a["estimate_minutes"] == 25

    task_b = rows["Task B"]
    assert task_b["task_id"] == john_task_with_category["id"]
    assert task_b["category_id"] == john_category["id"]
    assert task_b["estimate_minutes"] is None


@pytest.mark.integration
def test_create_session_fails_if_user_doesnt_provide_credentials(client: TestClient):

    params = {
        "mode": "classic",
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    session_input = {"params": params}

    session_post_request = client.post("/sessions", json=session_input)

    assert session_post_request.status_code == 401


@pytest.mark.integration
def test_create_session_fails_if_user_provides_non_owned_task(
    client: TestClient, auth_headers, make_task
):
    john = auth_headers("john@example.com")
    john_task = make_task(john, title="Task A")

    jane = auth_headers("jane@example.com")

    params = {
        "mode": "classic",
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }
    session_tasks = [
        {"task_id": john_task["id"], "estimate_minutes": 25},
    ]

    session_input = {"params": params, "tasks": session_tasks}

    session_post_request = client.post("/sessions", json=session_input, headers=jane)

    assert session_post_request.status_code == 404


@pytest.mark.integration
def test_create_session_fails_if_params_are_invalid(
    client: TestClient, auth_headers, make_task
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")
    john_task = make_task(john, title="Task A")

    params = {
        "mode": "incremental",
        "start_minutes": 25,
        "cap_minutes": 5,
        "growth": 2,
        "num_of_rounds": 3,
    }

    session_tasks = [
        {"task_id": john_task["id"], "estimate_minutes": 25},
    ]

    session_input = {"params": params, "tasks": session_tasks}

    session_post_request = client.post("/sessions", json=session_input, headers=jane)

    assert session_post_request.status_code == 422

    response_body = session_post_request.json()

    detail = response_body["detail"][0]

    assert detail["type"] == "pomodoro_validation_error"


@pytest.mark.integration
@pytest.mark.parametrize(
    "extra_body",
    [
        pytest.param({}, id="without_task_key"),
        pytest.param({"tasks": []}, id="empty_task_list"),
    ],
)
def test_create_session_without_tasks(client: TestClient, auth_headers, extra_body):
    john = auth_headers("john@example.com")

    params = {
        "mode": "classic",
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    session_input = {"params": params, **extra_body}

    session_post_request = client.post("/sessions", json=session_input, headers=john)

    assert session_post_request.status_code == 201

    session_json = session_post_request.json()

    assert session_json["session_tasks"] == []
    assert session_json["status"] == "active"

    planned_config = session_json["planned_config"]

    assert planned_config["params"] == params


@pytest.mark.integration
def test_create_session_fails_if_tasks_are_duplicated(
    client: TestClient, auth_headers, make_task
):
    john = auth_headers("john@example.com")
    john_task = make_task(john, title="Task A")

    task_id = john_task["id"]

    params = {
        "mode": "classic",
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    session_input = {
        "params": params,
        "tasks": [{"task_id": task_id}, {"task_id": task_id}],
    }

    session_post_request = client.post("/sessions", json=session_input, headers=john)

    assert session_post_request.status_code == 422

    detail = session_post_request.json()["detail"][0]

    assert detail["type"] == "value_error"
    assert detail["loc"] == ["body"]

    assert "duplicated tasks" in detail["msg"].lower()


@pytest.mark.integration
@pytest.mark.parametrize(
    "estimate_minutes",
    [
        pytest.param(0, id="zero"),
        pytest.param(-5, id="negative"),
    ],
)
def test_create_session_fails_if_estimate_minutes_is_invalid(
    client: TestClient, auth_headers, make_task, estimate_minutes
):
    john = auth_headers("john@example.com")
    john_task = make_task(john, title="Task A")
    task_id = john_task["id"]

    params = {
        "mode": "classic",
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    session_tasks = [{"task_id": task_id, "estimate_minutes": estimate_minutes}]

    session_input = {"params": params, "tasks": session_tasks}

    session_post_request = client.post("/sessions", json=session_input, headers=john)

    assert session_post_request.status_code == 422

    detail = session_post_request.json()["detail"][0]
    assert detail["type"] == "greater_than"
    assert detail["loc"] == ["body", "tasks", 0, "estimate_minutes"]
