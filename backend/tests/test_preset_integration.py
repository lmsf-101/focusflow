import pytest
from fastapi.testclient import TestClient

from focusflow_api.models import PomodoroMode


# Verificar que se crea preset de Pomodoro con los argumentos correctos
@pytest.mark.integration
def test_new_preset_is_created_successfully(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")

    preset_input = {
        "name": "preset-test",
        "mode": PomodoroMode.CLASSIC,
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    response = client.post("/presets", json=preset_input, headers=john)

    assert response.status_code == 201

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["name"] == preset_input["name"]
    assert data["mode"] == preset_input["mode"]


# Verificar que falla la creación de preset si no hay credenciales
@pytest.mark.integration
def test_new_preset_is_rejected_if_there_are_no_credentials(client: TestClient):

    preset_input = {
        "name": "preset-test",
        "mode": PomodoroMode.CLASSIC,
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    response = client.post("/presets", json=preset_input)

    assert response.status_code == 401


# Verificar que no se permite presets con el mismo nombre para el mismo usuario
@pytest.mark.integration
def test_duplicated_preset_name_get_rejected(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")

    first_preset = {
        "name": "preset-test",
        "mode": PomodoroMode.CLASSIC,
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    second_preset = {
        "name": "preset-test",
        "mode": PomodoroMode.INCREMENTAL,
        "start_minutes": 20,
        "growth": 2,
        "cap_minutes": 30,
        "num_of_rounds": 4,
    }

    first_response = client.post("/presets", json=first_preset, headers=john)

    assert first_response.status_code == 201
    assert isinstance(first_response.json()["id"], int)

    second_response = client.post("/presets", json=second_preset, headers=john)

    assert second_response.status_code == 409


# Verificar que presets con el mismo nombre es valido para diferentes usuarios
@pytest.mark.integration
def test_duplicated_preset_name_is_valid_for_different_users(
    client: TestClient, auth_headers
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    john_preset = {
        "name": "preset-test",
        "mode": PomodoroMode.CLASSIC,
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    jane_preset = {
        "name": "preset-test",
        "mode": PomodoroMode.INCREMENTAL,
        "start_minutes": 20,
        "growth": 2,
        "cap_minutes": 30,
        "num_of_rounds": 4,
    }

    john_response = client.post("/presets", json=john_preset, headers=john)

    assert john_response.status_code == 201
    assert isinstance(john_response.json()["id"], int)

    jane_response = client.post("/presets", json=jane_preset, headers=jane)

    assert jane_response.status_code == 201
    assert isinstance(jane_response.json()["id"], int)


# Verificar que creación de preset falla si se intenta asignar un proyecto en el que el usuario no es propetario
@pytest.mark.integration
def test_new_preset_is_rejected_if_project_is_not_owned_by_user(
    client: TestClient, auth_headers, make_project
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    john_project_id = make_project(john)["id"]

    jane_preset = {
        "name": "preset-test",
        "mode": PomodoroMode.CLASSIC,
        "project_id": john_project_id,
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    response = client.post("/presets", json=jane_preset, headers=jane)

    assert response.status_code == 404


# Verificar que creación de preset falla si se intenta asignar una categoria en el que el usuario no es propetario
@pytest.mark.integration
def test_new_preset_is_rejected_if_category_is_not_owned_by_user(
    client: TestClient, auth_headers, make_category
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    john_category_id = make_category(john)["id"]

    jane_preset = {
        "name": "preset-test",
        "mode": PomodoroMode.CLASSIC,
        "category_id": john_category_id,
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    response = client.post("/presets", json=jane_preset, headers=jane)

    assert response.status_code == 404


# Verificar que solicitud GET devuelve los presets del usuario
@pytest.mark.integration
def test_get_preset_returns_list_created_by_user(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    john_preset = {
        "name": "john-preset",
        "mode": PomodoroMode.CLASSIC,
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    jane_preset = {
        "name": "jane-preset",
        "mode": PomodoroMode.INCREMENTAL,
        "start_minutes": 20,
        "growth": 2,
        "cap_minutes": 30,
        "num_of_rounds": 4,
    }

    client.post("/presets", json=john_preset, headers=john)
    client.post("/presets", json=jane_preset, headers=jane)

    get_john_presets = client.get("/presets", headers=john)
    get_jane_presets = client.get("/presets", headers=jane)

    john_presets = get_john_presets.json()
    jane_presets = get_jane_presets.json()

    assert [p["name"] for p in john_presets] == [john_preset["name"]]
    assert [p["name"] for p in jane_presets] == [jane_preset["name"]]
