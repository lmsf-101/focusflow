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


# Verificar que solicitud GET /preset/{id} devuelve el preset especifico al dueño
@pytest.mark.integration
def test_get_preset_by_id(client: TestClient, auth_headers, make_preset):
    john = auth_headers("john@example.com")

    john_preset = make_preset(john)

    get_john_preset_response = client.get(f"/presets/{john_preset['id']}", headers=john)

    assert get_john_preset_response.status_code == 200

    assert get_john_preset_response.json() == john_preset


# Verificar que solicitud GET /preset/{id} falla para usuario que no sea dueño
@pytest.mark.integration
def test_get_preset_by_id_fails_if_user_is_not_the_preset_owner(
    client: TestClient, auth_headers, make_preset
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")
    john_preset = make_preset(john)

    get_john_preset_as_jane = client.get(f"/presets/{john_preset['id']}", headers=jane)

    assert get_john_preset_as_jane.status_code == 404


# Verificar que PATCH de preset funcione para cambiar el nombre del mismo
@pytest.mark.integration
def test_patch_preset_for_changing_preset_name(
    client: TestClient, auth_headers, make_preset
):
    NEW_NAME = "test-preset-2"
    john = auth_headers("john@example.com")

    john_preset = make_preset(john)

    new_name_input = {"name": NEW_NAME}

    response = client.patch(
        f"/presets/{john_preset['id']}", json=new_name_input, headers=john
    )

    assert response.status_code == 200
    assert response.json()["name"] == NEW_NAME


# Verificar que PATCH falle cuando se intenta pasar un parametro que no sea parte del mode (incremental)
@pytest.mark.integration
def test_patch_preset_fails_if_parameter_is_not_valid_for_mode(
    client: TestClient, auth_headers, make_preset
):
    john = auth_headers("john@example.com")

    john_preset = make_preset(john, mode="incremental")

    invalid_input = {"break_minutes": 5}

    response = client.patch(
        f"/presets/{john_preset['id']}", json=invalid_input, headers=john
    )

    assert response.status_code == 422

    # Ver detalles de la respuesta y verificar si trata de argumentos invalidos
    detail = response.json()["detail"][0]

    assert detail["type"] == "value_error"
    assert "incremental" in detail["msg"]
    assert "break_minutes" in detail["msg"]


# Verificar que PATCH falla cuando se intenta romper una restricción / condición del modo (cap_minutes < start_minutes para incremental)
@pytest.mark.integration
def test_patch_preset_fails_if_mode_constraint_is_broken(
    client: TestClient, auth_headers, make_preset
):
    john = auth_headers("john@example.com")

    john_preset = make_preset(john, mode="incremental")
    og_cap_minutes = john_preset["cap_minutes"]

    input_with_broken_constraints = {"cap_minutes": 10}

    response = client.patch(
        f"/presets/{john_preset['id']}",
        json=input_with_broken_constraints,
        headers=john,
    )

    assert response.status_code == 422

    # Revisar que el 422 no debe dejar el preset modificado a medias
    get_preset_response = client.get(f"/presets/{john_preset['id']}", headers=john)

    preset_cap_minutes = get_preset_response.json()["cap_minutes"]

    assert preset_cap_minutes == og_cap_minutes


# Verificar que PATCH falla cuando se intenta cambiar el modo (no esta permitido)
@pytest.mark.integration
def test_patch_preset_fails_if_update_tries_to_change_mode(
    client: TestClient, auth_headers, make_preset
):
    john = auth_headers("john@example.com")

    john_preset = make_preset(john, mode="classic")

    input_with_mode_change = {"mode": PomodoroMode.INCREMENTAL}

    response = client.patch(
        f"/presets/{john_preset['id']}", json=input_with_mode_change, headers=john
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "extra_forbidden"


# Verificar que PATCH falla cuando se intenta ingresar un nombre de preset duplicado
@pytest.mark.integration
def test_patch_preset_fails_if_new_name_is_a_duplicate(
    client: TestClient, auth_headers, make_preset
):

    NAME_TO_DUPLICATE = "preset1"

    john = auth_headers("john@example.com")

    _ = make_preset(john, mode="classic", name=NAME_TO_DUPLICATE)
    preset2 = make_preset(john, mode="incremental", name="preset2")

    input_with_duplicated_name = {"name": NAME_TO_DUPLICATE}

    response = client.patch(
        f"/presets/{preset2['id']}", json=input_with_duplicated_name, headers=john
    )

    assert response.status_code == 409


# Verificar que PATCH falla cuando se intenta actualizar un preset ajeno
@pytest.mark.integration
def test_patch_preset_fails_if_update_is_for_non_owned_preset(
    client: TestClient, auth_headers, make_preset
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    john_preset = make_preset(john)

    jane_input = {"name": "jane_preset"}

    response = client.patch(
        f"/presets/{john_preset['id']}", json=jane_input, headers=jane
    )

    assert response.status_code == 404


# Verificar que PATCH falla cuando se intenta asignar a un preset un ID de proyecto ajeno al usuario
@pytest.mark.integration
def test_patch_preset_fails_if_update_includes_a_non_owned_project_id(
    client: TestClient, auth_headers, make_project, make_preset
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    jane_project = make_project(jane)
    john_preset = make_preset(john)

    invalid_project_input = {"project_id": jane_project["id"]}

    response = client.patch(
        f"/presets/{john_preset['id']}", json=invalid_project_input, headers=john
    )

    assert response.status_code == 404

    # Revisar si preset no se haya modificado
    get_preset_response = client.get(f"/presets/{john_preset['id']}", headers=john)

    assert get_preset_response.status_code == 200
    assert get_preset_response.json()["project_id"] is None


# Verificar que PATCH falla cuando se intenta asignar a un preset un ID de categoria ajeno al usuario
@pytest.mark.integration
def test_patch_preset_fails_if_update_includes_a_non_owned_category_id(
    client: TestClient, auth_headers, make_category, make_preset
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    jane_category = make_category(jane)
    john_preset = make_preset(john)

    invalid_category_input = {"category_id": jane_category["id"]}

    response = client.patch(
        f"/presets/{john_preset['id']}", json=invalid_category_input, headers=john
    )

    assert response.status_code == 404

    # Revisar si preset no se haya modificado
    get_preset_response = client.get(f"/presets/{john_preset['id']}", headers=john)

    assert get_preset_response.status_code == 200
    assert get_preset_response.json()["category_id"] is None


# Verificar que PATCH con project_id = null elimina la etiqueta del proyecto
@pytest.mark.integration
def test_patch_preset_removes_project_with_null_id(
    client: TestClient, auth_headers, make_project, make_preset
):

    john = auth_headers("john@example.com")
    john_project = make_project(john)
    john_preset = make_preset(john, project_id=john_project["id"])

    remove_project_input = {"project_id": None}

    response = client.patch(
        f"/presets/{john_preset['id']}", json=remove_project_input, headers=john
    )

    assert response.status_code == 200
    assert response.json()["project_id"] is None


# Verificar que PATCH con category_id = null elimina la categoría del preset
@pytest.mark.integration
def test_patch_preset_removes_category_with_null_id(
    client: TestClient, auth_headers, make_category, make_preset
):

    john = auth_headers("john@example.com")
    john_category = make_category(john)
    john_preset = make_preset(john, category_id=john_category["id"])

    remove_category_input = {"category_id": None}

    response = client.patch(
        f"/presets/{john_preset['id']}", json=remove_category_input, headers=john
    )

    assert response.status_code == 200
    assert response.json()["category_id"] is None


# Verificar que solicitud DELETE /preset/{id} elimina preset para el dueño
@pytest.mark.integration
def test_delete_preset_by_id(client: TestClient, auth_headers, make_preset):
    john = auth_headers("john@example.com")
    john_preset = make_preset(john)

    delete_preset_response = client.delete(
        f"/presets/{john_preset['id']}", headers=john
    )

    assert delete_preset_response.status_code == 204

    # Revisar si GET preset ya no existe (404)
    get_preset_response = client.get(f"/presets/{john_preset['id']}", headers=john)

    assert get_preset_response.status_code == 404


# Verificar que solicitud DELETE /preset/{id} NO elimina el preset si el usuario no es dueño de ella
@pytest.mark.integration
def test_delete_preset_by_id_fails_if_user_is_not_preset_owner(
    client: TestClient, auth_headers, make_preset
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")
    john_preset = make_preset(john)

    delete_john_preset_as_jane = client.delete(
        f"/presets/{john_preset['id']}", headers=jane
    )

    assert delete_john_preset_as_jane.status_code == 404

    # Revisar si preset todavia existe

    get_john_preset_response = client.get(f"/presets/{john_preset['id']}", headers=john)

    assert get_john_preset_response.status_code == 200
