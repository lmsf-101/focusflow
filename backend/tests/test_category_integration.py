import pytest
from fastapi.testclient import TestClient


# Verificar que se crea category con ID y nombre de forma exitosa
@pytest.mark.integration
def test_new_category_is_created_successfully(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")
    category_name = "Category Example"

    response = client.post("/categories", json={"name": category_name}, headers=john)

    assert response.status_code == 201

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["name"] == category_name


# Verifica que solicitud GET permite recuperar category por ID para el dueño
@pytest.mark.integration
def test_get_category_by_id_returns_category_for_owner(
    client: TestClient, auth_headers, make_category
):

    john = auth_headers("john@example.com")
    category_name = "Category Example"
    create_category_json = make_category(john, name=category_name)

    category_id = create_category_json["id"]

    response = client.get(f"/categories/{category_id}", headers=john)

    assert response.status_code == 200
    assert response.json()["name"] == category_name


# Verificar que PATCH permite al dueño modificar el nombre de una categoria
@pytest.mark.integration
def test_patch_category_updates_name_for_owner(
    client: TestClient, auth_headers, make_category
):

    original_name = "Test Category"
    new_name = "MY category"
    john = auth_headers("john@example.com")
    create_category_json = make_category(john, name=original_name)
    category_id = create_category_json["id"]

    update_response = client.patch(
        f"/categories/{category_id}", json={"name": new_name}, headers=john
    )
    update_response_data = update_response.json()

    assert update_response.status_code == 200
    assert update_response_data["name"] == new_name
    assert update_response_data["id"] == category_id

    get_response = client.get(f"/categories/{category_id}", headers=john)

    assert get_response.json()["name"] == new_name


# Verificar que una solicitud PATCH vacia no tiene efecto a la categoria
@pytest.mark.integration
def test_patch_with_empty_body_changes_nothing_in_category(
    client: TestClient, auth_headers, make_category
):
    category_name = "Test Category 2"
    john = auth_headers("john@example.com")

    create_category_json = make_category(john, name=category_name)
    category_id = create_category_json["id"]

    update_response = client.patch(f"/categories/{category_id}", json={}, headers=john)
    assert update_response.status_code == 200

    update_response_data = update_response.json()

    assert update_response_data["name"] == category_name

    get_response = client.get(f"/categories/{category_id}", headers=john)

    assert get_response.json()["name"] == category_name


# Verificar que solicitud PATCH es rechazado si tiene nombre invalido (null, vacio)
@pytest.mark.integration
@pytest.mark.parametrize("invalid_body", [{"name": ""}, {"name": None}])
def test_patch_rejects_invalid_name_for_category(
    client: TestClient, auth_headers, make_category, invalid_body
):
    category_name = "Test Category"
    john = auth_headers("john@example.com")

    create_category_json = make_category(john, name=category_name)
    category_id = create_category_json["id"]

    update_response = client.patch(
        f"/categories/{category_id}", json=invalid_body, headers=john
    )

    assert update_response.status_code == 422

    get_response = client.get(f"/categories/{category_id}", headers=john)

    assert get_response.json()["name"] == category_name


# Verificar que solicitud DELETE elimina la categoria correctamente, con credenciales e ID correcto
@pytest.mark.integration
def test_delete_category_removes_it_for_owner(
    client: TestClient, auth_headers, make_category
):
    category_name = "Test Category"
    john = auth_headers("john@example.com")

    create_category_json = make_category(john, name=category_name)
    category_id = create_category_json["id"]

    delete_response = client.delete(f"/categories/{category_id}", headers=john)

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_project_response = client.get(f"/categories/{category_id}", headers=john)

    assert get_project_response.status_code == 404

    get_projects_response = client.get("/categories", headers=john)

    assert get_projects_response.json() == []


# Verificar que GET categories no se procese sin cabecera
@pytest.mark.integration
def test_get_categories_is_invalid_without_auth_header(client: TestClient):
    response = client.get("/categories")

    assert response.status_code == 401


# Verificar solicitud GET /categories regresa una lista para el dueño correcto
@pytest.mark.integration
def test_get_categories_returns_list_for_owner(client: TestClient, auth_headers):
    john = auth_headers("john@example.com")
    category_name = "Test Category"

    client.post("/categories", json={"name": category_name}, headers=john)

    response = client.get("/categories", headers=john)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["name"] == category_name


# Verificar solicitud GET /categories regresa una lista vacia para usuario ajeno
@pytest.mark.integration
def test_get_categories_returns_empty_for_another_user(
    client: TestClient, auth_headers
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    category_name = "Test Category"

    client.post("/categories", json={"name": category_name}, headers=john)

    response = client.get("/categories", headers=jane)

    assert response.status_code == 200
    assert response.json() == []


# Verificar que GET categories/{category_id} sea rechazado si el usuario no es dueño de ella
@pytest.mark.integration
def test_get_category_by_id_is_reject_for_non_owner(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    category_name = "Test Category"

    post_response = client.post(
        "/categories", json={"name": category_name}, headers=john
    )

    category_id = post_response.json()["id"]

    response = client.get(f"/categories/{category_id}", headers=jane)

    assert response.status_code == 404


# Verificar que PATCH categories/{category_id} no tenga efecto si el usuario no es dueño de ella
@pytest.mark.integration
def test_patch_category_by_id_does_nothing_for_non_owner(
    client: TestClient, auth_headers
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    category_name = "Test Category"

    post_response = client.post(
        "/categories", json={"name": category_name}, headers=john
    )

    category_id = post_response.json()["id"]

    response = client.patch(
        f"/categories/{category_id}", json={"name": "MY category"}, headers=jane
    )

    assert response.status_code == 404

    # Validar que no hubo cambio de nombre a la categoria:
    get_project_response = client.get(f"/categories/{category_id}", headers=john)

    assert get_project_response.status_code == 200
    assert get_project_response.json()["name"] == category_name


# Verificar que DELETE categories/{category_id} NO borra la categoria si el usuario no es dueño de ella
@pytest.mark.integration
def test_delete_category_by_id_does_not_delete_for_non_owner(
    client: TestClient, auth_headers
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    category_name = "Test Category"

    post_response = client.post(
        "/categories", json={"name": category_name}, headers=john
    )

    category_id = post_response.json()["id"]

    response = client.delete(f"/categories/{category_id}", headers=jane)

    assert response.status_code == 404

    # Validar que no se borró la categoria:
    get_project_response = client.get(f"/categories/{category_id}", headers=john)

    assert get_project_response.status_code == 200
    assert isinstance(get_project_response.json()["id"], int)
    assert get_project_response.json()["name"] == category_name
