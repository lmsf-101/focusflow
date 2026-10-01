import pytest
from fastapi.testclient import TestClient


# Verificar que se crea proyecto con ID y nombre de forma exitosa
@pytest.mark.integration
def test_new_project_is_created_successfully(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")
    project_name = "Test Proyect"

    response = client.post("/projects", json={"name": project_name}, headers=john)

    assert response.status_code == 201

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["name"] == project_name


# Verifica que solicitud GET permite recuperar proyecto por ID para el dueño
@pytest.mark.integration
def test_get_project_by_id_returns_project_for_owner(
    client: TestClient, auth_headers, make_project
):

    project_name = "Test 1"
    john = auth_headers("john@example.com")
    create_project_json = make_project(john, name=project_name)

    project_id = create_project_json["id"]

    response = client.get(f"/projects/{project_id}", headers=john)

    assert response.status_code == 200
    assert response.json()["name"] == project_name


# Verificar que PATCH permite al dueño modificar el nombre de un proyecto existente
# Revisar que la actualizacion (nuevo nombre) se ve reflejado en la BD
@pytest.mark.integration
def test_patch_project_updates_name_for_owner(
    client: TestClient, auth_headers, make_project
):

    original_name = "Test 1"
    new_name = "New Project"
    john = auth_headers("john@example.com")
    create_project_json = make_project(john, name=original_name)
    project_id = create_project_json["id"]

    update_response = client.patch(
        f"/projects/{project_id}", json={"name": new_name}, headers=john
    )
    update_response_data = update_response.json()

    assert update_response.status_code == 200
    assert update_response_data["name"] == new_name
    assert update_response_data["id"] == project_id

    get_response = client.get(f"/projects/{project_id}", headers=john)

    assert get_response.json()["name"] == new_name


# Verificar que una solicitud PATCH vacia no tiene efecto al proyecto
@pytest.mark.integration
def test_patch_with_empty_body_changes_nothing(
    client: TestClient, auth_headers, make_project
):
    project_name = "Test 1"
    john = auth_headers("john@example.com")

    create_project_json = make_project(john, name=project_name)
    project_id = create_project_json["id"]

    update_response = client.patch(f"/projects/{project_id}", json={}, headers=john)
    assert update_response.status_code == 200

    update_response_data = update_response.json()

    assert update_response_data["name"] == project_name

    get_response = client.get(f"/projects/{project_id}", headers=john)

    assert get_response.json()["name"] == project_name


# Verificar que solicitud PATCH es rechazado si tiene nombre invalido (null, vacio)
@pytest.mark.integration
@pytest.mark.parametrize("invalid_body", [{"name": ""}, {"name": None}])
def test_patch_rejects_invalid_name(
    client: TestClient, auth_headers, make_project, invalid_body
):
    project_name = "Test 1"
    john = auth_headers("john@example.com")

    create_project_json = make_project(john, name=project_name)
    project_id = create_project_json["id"]

    update_response = client.patch(
        f"/projects/{project_id}", json=invalid_body, headers=john
    )

    assert update_response.status_code == 422

    get_response = client.get(f"/projects/{project_id}", headers=john)

    assert get_response.json()["name"] == project_name


# Verificar que solicitud DELETE elimina el proyecto correctamente, con credenciales e ID correcto
# Revisar si recuperar el proyecto eliminado regresa 404, y evaluar que la lista de proyectos
# este vacia
@pytest.mark.integration
def test_delete_project_removes_it_for_owner(
    client: TestClient, auth_headers, make_project
):
    project_name = "Test 1"
    john = auth_headers("john@example.com")

    create_project_json = make_project(john, name=project_name)
    project_id = create_project_json["id"]

    delete_response = client.delete(f"/projects/{project_id}", headers=john)

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_project_response = client.get(f"/projects/{project_id}", headers=john)

    assert get_project_response.status_code == 404

    get_projects_response = client.get("/projects", headers=john)

    assert get_projects_response.json() == []


# Verificar que GET projects no se procese sin cabecera
@pytest.mark.integration
def test_get_projects_is_invalid_without_auth_header(client: TestClient):
    response = client.get("/projects")

    assert response.status_code == 401


# Verificar solicitud GET /projects regresa una lista para el dueño correcto
@pytest.mark.integration
def test_get_projects_returns_list_for_owner(client: TestClient, auth_headers):
    john = auth_headers("john@example.com")
    project_name = "Test Project"

    client.post("/projects", json={"name": project_name}, headers=john)

    response = client.get("/projects", headers=john)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["name"] == project_name


# Verificar solicitud GET a projects que regresa una lista vacia para usuario ajeno
@pytest.mark.integration
def test_get_project_returns_empty_for_another_user(client: TestClient, auth_headers):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    project_name = "Test Project"

    client.post("/projects", json={"name": project_name}, headers=john)

    response = client.get("/projects", headers=jane)

    assert response.status_code == 200
    assert response.json() == []


# Verificar que GET project/{project_id} sea rechazado si el usuario no es dueño de ella
@pytest.mark.integration
def test_get_project_by_id_is_reject_for_non_owner(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    project_name = "Test Project"

    post_response = client.post("/projects", json={"name": project_name}, headers=john)

    project_id = post_response.json()["id"]

    response = client.get(f"/projects/{project_id}", headers=jane)

    assert response.status_code == 404


# Verificar que PATCH project/{project_id} no tenga efecto si el usuario no es dueño de ella
@pytest.mark.integration
def test_patch_project_by_id_does_nothing_for_non_owner(
    client: TestClient, auth_headers
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    project_name = "Test Project"

    post_response = client.post("/projects", json={"name": project_name}, headers=john)

    project_id = post_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}", json={"name": "MY project"}, headers=jane
    )

    assert response.status_code == 404

    # Validar que no hubo cambio de nombre al proyecto:
    get_project_response = client.get(f"/projects/{project_id}", headers=john)

    assert get_project_response.status_code == 200
    assert get_project_response.json()["name"] == project_name


# Verificar que DELETE project/{project_id} borré el proyecto si el usuario no es dueño de ella
@pytest.mark.integration
def test_delete_project_by_id_does_not_delete_for_non_owner(
    client: TestClient, auth_headers
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    project_name = "Test Project"

    post_response = client.post("/projects", json={"name": project_name}, headers=john)

    project_id = post_response.json()["id"]

    response = client.delete(f"/projects/{project_id}", headers=jane)

    assert response.status_code == 404

    # Validar que no hubo cambio de nombre al proyecto:
    get_project_response = client.get(f"/projects/{project_id}", headers=john)

    assert get_project_response.status_code == 200
    assert isinstance(get_project_response.json()["id"], int)
    assert get_project_response.json()["name"] == project_name
