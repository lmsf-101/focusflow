import pytest
from fastapi.testclient import TestClient


# Rechazar la creacion de una tarea si el proyecto asignado no es del usuario
@pytest.mark.integration
def test_create_task_with_foreign_project_is_rejected(
    client: TestClient, auth_headers, make_project
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    jane_project = make_project(jane)

    response = client.post(
        "/tasks",
        json={"title": "My task", "priority": "low", "project_id": jane_project["id"]},
        headers=john,
    )

    assert response.status_code == 404
    assert client.get("/tasks", headers=john).json() == []


# Rechazar la creacion de una tarea si la categoria asignada no es del usuario
@pytest.mark.integration
def test_create_task_with_foreign_category_is_rejected(
    client: TestClient, auth_headers, make_category
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    jane_category = make_category(jane)

    response = client.post(
        "/tasks",
        json={
            "title": "My task",
            "priority": "low",
            "category_id": jane_category["id"],
        },
        headers=john,
    )

    assert response.status_code == 404
    assert client.get("/tasks", headers=john).json() == []


# Rechazar la actualizacion de una tarea si se asigna un proyecto que no sea del usuario
@pytest.mark.integration
def test_update_task_with_foreign_project_is_rejected(
    client: TestClient, auth_headers, make_task, make_project
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    john_task = make_task(john)

    jane_project = make_project(jane)

    response = client.patch(
        f"/tasks/{john_task['id']}",
        json={"project_id": jane_project["id"]},
        headers=john,
    )

    assert response.status_code == 404
    assert (
        client.get(f"/tasks/{john_task['id']}", headers=john).json()["project_id"]
        is None
    )


# Rechazar la actualizacion de una tarea si se asigna una categoria que no sea del usuario
@pytest.mark.integration
def test_update_task_with_foreign_category_is_rejected(
    client: TestClient, auth_headers, make_task, make_category
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    john_task = make_task(john)
    jane_category = make_category(jane)

    response = client.patch(
        f"/tasks/{john_task['id']}",
        json={"category_id": jane_category["id"]},
        headers=john,
    )

    assert response.status_code == 404
    assert (
        client.get(f"/tasks/{john_task['id']}", headers=john).json()["category_id"]
        is None
    )


# Actualizacion a tarea sin nueva clave de proyecto mantiene
# intacto al proyecto previamente asignado
@pytest.mark.integration
def test_update_task_without_project_key_leaves_project_untouched(
    client: TestClient, auth_headers, make_project, make_task
):
    john = auth_headers("john@example.com")
    first_project = make_project(john)
    task = make_task(john, project_id=first_project["id"])

    new_title = "New task title"

    response = client.patch(
        f"/tasks/{task['id']}", json={"title": new_title}, headers=john
    )

    assert response.status_code == 200
    assert response.json()["title"] == new_title
    assert response.json()["project_id"] == first_project["id"]


# Actualizacion a tarea que elimina el proyecto asignado
# con clave nulo (None)
@pytest.mark.integration
def test_update_task_with_null_project_key_unassigns_project(
    client: TestClient, auth_headers, make_project, make_task
):
    john = auth_headers("john@example.com")
    first_project = make_project(john)
    task = make_task(john, project_id=first_project["id"])

    response = client.patch(
        f"/tasks/{task['id']}", json={"project_id": None}, headers=john
    )

    assert response.status_code == 200
    assert client.get(f"/tasks/{task['id']}", headers=john).json()["project_id"] is None


# Verificar que tarea se asocia a un nuevo proyecto
# mediante la actualizacion del ID del proyecto
@pytest.mark.integration
def test_update_task_with_own_project_assigns_it(
    client: TestClient, auth_headers, make_project, make_task
):
    john = auth_headers("john@example.com")
    first_project = make_project(john)
    task = make_task(john)

    response = client.patch(
        f"/tasks/{task['id']}", json={"project_id": first_project["id"]}, headers=john
    )

    assert response.status_code == 200
    assert response.json()["project_id"] == first_project["id"]


# Verificar que el estado predeterminado de una tarea se asigna correctamente
@pytest.mark.integration
def test_create_task_defaults_status_to_pending_with_project_and_category_empty(
    client: TestClient, auth_headers, make_task
):
    john = auth_headers("john@example.com")

    task = make_task(john)  #  Status ausente

    assert task["status"] == "pending"
    assert task["project_id"] is None
    assert task["category_id"] is None


# Verificar que GET /tasks no se procese sin cabecera
@pytest.mark.integration
def test_get_tasks_is_invalid_without_auth_header(client: TestClient):
    response = client.get("/tasks")

    assert response.status_code == 401


# Verificar que GET /tasks regresa una lista para el dueño correcto
@pytest.mark.integration
def test_get_tasks_returns_list_for_owner(client: TestClient, auth_headers, make_task):
    john = auth_headers("john@example.com")
    task_title = "My task"

    make_task(john, title=task_title)

    response = client.get("/tasks", headers=john)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["title"] == task_title


# Verificar que GET /tasks regresa una lista vacia para usuario ajeno
@pytest.mark.integration
def test_get_tasks_returns_empty_for_another_user(
    client: TestClient, auth_headers, make_task
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    make_task(john)

    response = client.get("/tasks", headers=jane)

    assert response.status_code == 200
    assert response.json() == []


# Verificar que GET /tasks/{task_id} regresa la tarea a su dueño
@pytest.mark.integration
def test_get_task_by_id_returns_it_for_owner(
    client: TestClient, auth_headers, make_task
):
    john = auth_headers("john@example.com")
    task_title = "My task"

    task = make_task(john, title=task_title)

    response = client.get(f"/tasks/{task['id']}", headers=john)

    assert response.status_code == 200
    assert response.json()["title"] == task_title
    assert response.json()["id"] == task["id"]


# Verificar que GET /tasks/{task_id} sea rechazado si el usuario no es dueño de ella.
# (regresa código 404)
@pytest.mark.integration
def test_get_task_by_id_is_rejected_for_non_owner(
    client: TestClient, auth_headers, make_task
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    john_task = make_task(john)

    response = client.get(f"/tasks/{john_task['id']}", headers=jane)

    assert response.status_code == 404


# Verificar que PATCH /tasks/{task_id} sea rechazado si el usuario no es dueño de ella
@pytest.mark.integration
def test_update_task_is_rejected_for_non_owner(
    client: TestClient, auth_headers, make_task
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    original_title = "My task"
    john_task = make_task(john, title=original_title)

    response = client.patch(
        f"/tasks/{john_task['id']}", json={"title": "Hijacked"}, headers=jane
    )

    assert response.status_code == 404
    assert (
        client.get(f"/tasks/{john_task['id']}", headers=john).json()["title"]
        == original_title
    )


# Verificar que DELETE /tasks/{task_id} sea rechazado si el usuario no es dueño de ella
@pytest.mark.integration
def test_delete_task_is_rejected_for_non_owner(
    client: TestClient, auth_headers, make_task
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    john_task = make_task(john)

    response = client.delete(f"/tasks/{john_task['id']}", headers=jane)

    assert response.status_code == 404
    assert client.get(f"/tasks/{john_task['id']}", headers=john).status_code == 200


# Verificar que solicitud DELETE elimina la tarea correctamente,
# con credenciales e ID correcto
@pytest.mark.integration
def test_delete_task_removes_it_for_owner(client: TestClient, auth_headers, make_task):
    john = auth_headers("john@example.com")

    task = make_task(john)
    task_id = task["id"]

    delete_response = client.delete(f"/tasks/{task_id}", headers=john)

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_task_response = client.get(f"/tasks/{task_id}", headers=john)

    assert get_task_response.status_code == 404

    get_tasks_response = client.get("/tasks", headers=john)

    assert get_tasks_response.json() == []


# Verificar que el titulo de una tarea nueva entra entre
# limites permitidos
@pytest.mark.integration
@pytest.mark.parametrize(
    "title, expected",
    [
        ("", 422),
        ("a" * 100, 201),
        ("a" * 101, 422),
    ],
)
def test_create_task_title_length_limits(
    client: TestClient, auth_headers, title, expected
):
    john = auth_headers("john@example.com")

    response = client.post(
        "/tasks", json={"title": title, "priority": "low"}, headers=john
    )

    assert response.status_code == expected
