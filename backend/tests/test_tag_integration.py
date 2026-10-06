import pytest
from fastapi.testclient import TestClient


# Verificar que se crea tag con ID y nombre de forma exitosa
@pytest.mark.integration
def test_new_tag_is_created_successfully(client: TestClient, auth_headers):

    john = auth_headers("john@example.com")
    tag_name = "urgent"

    response = client.post("/tags", json={"name": tag_name}, headers=john)

    assert response.status_code == 201

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["name"] == tag_name


# Verifica que solicitud GET permite recuperar tag por ID para el dueño
@pytest.mark.integration
def test_get_tag_by_id_returns_tag_for_owner(
    client: TestClient, auth_headers, make_tag
):

    john = auth_headers("john@example.com")
    tag_name = "personal"
    tag_id = make_tag(john, name=tag_name)["id"]

    response = client.get(f"/tags/{tag_id}", headers=john)

    assert response.status_code == 200
    assert response.json()["name"] == tag_name


# Verificar que GET tags no se procese sin cabecera
@pytest.mark.integration
def test_get_tags_is_invalid_without_auth_header(client: TestClient):
    response = client.get("/tags")

    assert response.status_code == 401


# Verificar solicitud GET /tags regresa una lista para el dueño correcto
@pytest.mark.integration
def test_get_tags_returns_list_for_owner(client: TestClient, auth_headers, make_tag):
    john = auth_headers("john@example.com")
    tag_name = "personal"

    make_tag(john, name=tag_name)

    response = client.get("/tags", headers=john)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["name"] == tag_name


# Verificar solicitud GET /tags regresa una lista vacia para usuario ajeno
@pytest.mark.integration
def test_get_tags_returns_empty_for_another_user(
    client: TestClient, auth_headers, make_tag
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    make_tag(john)

    response = client.get("/tags", headers=jane)

    assert response.status_code == 200
    assert response.json() == []


# Verificar que GET tags/{tag_id} sea rechazado si el usuario no es dueño de ella
@pytest.mark.integration
def test_get_tag_by_id_is_rejected_for_non_owner(
    client: TestClient, auth_headers, make_tag
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    tag_id = make_tag(john)["id"]

    response = client.get(f"/tags/{tag_id}", headers=jane)

    assert response.status_code == 404


# Verificar que DELETE tags/{tag_id} NO borra la etiqueta si el usuario no es dueño de ella
@pytest.mark.integration
def test_delete_tag_by_id_does_not_delete_for_non_owner(
    client: TestClient, auth_headers, make_tag
):

    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")

    tag_name = "personal"
    tag_id = make_tag(john, name=tag_name)["id"]

    response = client.delete(f"/tags/{tag_id}", headers=jane)

    assert response.status_code == 404

    # Validar que no se borró la etiqueta:
    get_response = client.get(f"/tags/{tag_id}", headers=john)

    assert get_response.status_code == 200
    assert get_response.json()["name"] == tag_name


# Verificar que solicitud DELETE elimina la etiqueta correctamente, con credenciales e ID correcto
@pytest.mark.integration
def test_delete_tag_removes_it_for_owner(client: TestClient, auth_headers, make_tag):
    john = auth_headers("john@example.com")

    tag_id = make_tag(john)["id"]

    delete_response = client.delete(f"/tags/{tag_id}", headers=john)

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_tag_response = client.get(f"/tags/{tag_id}", headers=john)

    assert get_tag_response.status_code == 404

    get_tags_response = client.get("/tags", headers=john)

    assert get_tags_response.json() == []


# Verificar que, tras borrar una etiqueta, su nombre queda libre para crearla de nuevo
@pytest.mark.integration
def test_tag_name_can_be_reused_after_deleting_it(
    client: TestClient, auth_headers, make_tag
):
    john = auth_headers("john@example.com")
    tag_name = "urgent"

    tag_id = make_tag(john, name=tag_name)["id"]

    delete_response = client.delete(f"/tags/{tag_id}", headers=john)

    assert delete_response.status_code == 204

    recreate_response = client.post("/tags", json={"name": tag_name}, headers=john)

    assert recreate_response.status_code == 201
    assert recreate_response.json()["name"] == tag_name


# Verificar que no se duplique etiquetas con el mismo nombre para un solo usuario
# Verificar que solo haya una etiqueta
@pytest.mark.integration
def test_create_tag_with_duplicate_name_is_rejected(
    client: TestClient, auth_headers, make_tag
):
    john = auth_headers("john@example.com")
    tag_name = "urgent"

    make_tag(john, name=tag_name)["id"]

    duplicate_response = client.post("/tags", json={"name": tag_name}, headers=john)

    assert duplicate_response.status_code == 409

    get_tags_response = client.get("/tags", headers=john)

    assert get_tags_response.status_code == 200

    body = get_tags_response.json()

    assert len(body) == 1
    assert body[0]["name"] == tag_name


# Verificar la unicidad de etiquetas: Un usuario puede crear una etiqueta
# con el mismo nombre de una etiqueta creada por otro usuario
@pytest.mark.integration
def test_tag_with_same_name_can_be_created_for_different_users(
    client: TestClient, auth_headers, make_tag
):
    john = auth_headers("john@example.com")
    jane = auth_headers("jane@example.com")
    tag_name = "urgent"

    john_tag_id = make_tag(john, name=tag_name)["id"]

    jane_post_tag_response = client.post("/tags", json={"name": tag_name}, headers=jane)

    assert jane_post_tag_response.status_code == 201

    jane_tag_id = jane_post_tag_response.json()["id"]

    john_get_tag_response = client.get(f"/tags/{john_tag_id}", headers=john)
    assert john_get_tag_response.status_code == 200
    assert john_get_tag_response.json()["name"] == tag_name

    jane_get_tag_response = client.get(f"/tags/{jane_tag_id}", headers=jane)
    assert jane_get_tag_response.status_code == 200
    assert jane_get_tag_response.json()["name"] == tag_name


# Verificar que la normalización de las etiquetas funcione correctamente
# (sin espacio, minusculas)
@pytest.mark.integration
@pytest.mark.parametrize(
    "tag_name, expected_name",
    [
        ("    Urgente    ", "urgente"),
        ("  TEST   ", "test"),
        (" WiErD TAg  ", "wierd tag"),
    ],
)
def test_create_tag_normalizes_case_and_whitespace(
    client: TestClient, auth_headers, tag_name, expected_name
):
    john = auth_headers("john@example.com")

    response = client.post("/tags", json={"name": tag_name}, headers=john)

    assert response.status_code == 201

    assert response.json()["name"] == expected_name


# Verificar que la creacion de etiquetas invaliden nombres
# restringidos (solo espacios, vacio)
@pytest.mark.integration
@pytest.mark.parametrize("tag_name", ["    ", ""])
def test_create_tag_rejects_blank_name(client: TestClient, auth_headers, tag_name):
    john = auth_headers("john@example.com")

    response = client.post("/tags", json={"name": tag_name}, headers=john)

    assert response.status_code == 422
