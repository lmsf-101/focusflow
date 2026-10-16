import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")

os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "5")

os.environ["CORS_ORIGINS"] = '["http://localhost:5173"]'

import focusflow_api.models  # noqa: F401
from focusflow_api.app import create_app
from focusflow_api.config import get_settings
from focusflow_api.db import Base, get_db


# Fixture de base de datos (test_engine)
@pytest.fixture(scope="session")
def test_engine():

    settings = get_settings()

    test_db = f"{settings.postgres_db}_test"

    admin_url = settings.database_url.set(database="postgres")

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as conn:
        test_stmt = text("""
                SELECT 1 FROM pg_database
                WHERE datname = :nombre
                         """)

        test_result = conn.execute(test_stmt, {"nombre": test_db})

        if not (test_result.scalar_one_or_none()):
            create_db_stmt = text(f"CREATE DATABASE {test_db}")

            conn.execute(create_db_stmt)

    admin_engine.dispose()

    test_url = settings.database_url.set(database=test_db)

    test_engine = create_engine(test_url)

    Base.metadata.create_all(test_engine)

    yield test_engine

    test_engine.dispose()


# Fixture para abrir session con test_engine
@pytest.fixture(scope="function")
def db_session(test_engine):
    connection = test_engine.connect()

    trans = connection.begin()

    session = Session(connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()

    trans.rollback()

    connection.close()


# Fixture para generar cliente de prueba, con session hacia DB de prueba
@pytest.fixture(scope="function")
def client(db_session):
    app = create_app()

    app.dependency_overrides[get_db] = lambda: db_session

    yield TestClient(app)

    app.dependency_overrides.clear()


# Fixture para trabajar con usuario registrado
@pytest.fixture(scope="function")
def registered_user(client) -> dict[str, str]:
    credentials = {"email": "test@example.com", "password": "test123"}
    response = client.post("/register", json=credentials)

    assert response.status_code == 200, response.text

    return credentials


# Función que registra un usuario y da su cabecera Bearer.
@pytest.fixture(scope="function")
def auth_headers(client):
    """Devuelve una función que registra un usuario y da su cabecera Bearer."""

    def _for(email: str, password: str = "test123") -> dict[str, str]:
        client.post("/register", json={"email": email, "password": password})
        response = client.post("/token", data={"username": email, "password": password})
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _for


# Funcion que genera un nuevo proyecto a la base de datos a partir del token de auth
# y regresa sus datos
@pytest.fixture(scope="function")
def make_project(client):
    def _make(headers: dict[str, str], *, name: str = "Test Project") -> dict:
        response = client.post("/projects", json={"name": name}, headers=headers)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


# Funcion que genera una nueva categoria  a la base de datos a partir del token de auth
# y regresa sus datos
@pytest.fixture(scope="function")
def make_category(client):
    def _make(headers: dict[str, str], *, name: str = "Test Category") -> dict:
        response = client.post("/categories", json={"name": name}, headers=headers)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


# Funcion que genera una nueva etiqueta a partir del token de auth y regresa sus datos.
@pytest.fixture(scope="function")
def make_tag(client):
    def _make(headers: dict[str, str], *, name: str = "example-tag") -> dict:
        response = client.post("/tags", json={"name": name}, headers=headers)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


_OMIT = object()


# Funcion que genera una nueva tarea a partir del token de auth y regresa sus datos.
# Las claves con _OMIT no se mandan en el body
@pytest.fixture(scope="function")
def make_task(client):
    def _make(
        headers: dict[str, str],
        *,
        title: str = "Test Task",
        priority: str = "low",
        status=_OMIT,
        project_id=_OMIT,
        category_id=_OMIT,
        tag_ids=_OMIT,
    ) -> dict:
        body = {"title": title, "priority": priority}

        for key, value in (
            ("status", status),
            ("project_id", project_id),
            ("category_id", category_id),
            ("tag_ids", tag_ids),
        ):
            if value is not _OMIT:
                body[key] = value

        response = client.post("/tasks", json=body, headers=headers)
        assert response.status_code == 201, response.text
        return response.json()

    return _make
