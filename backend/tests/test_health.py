from fastapi.testclient import TestClient

from focusflow_api.app import create_app
from focusflow_api.config import Settings, get_settings


def test_health_returns_ok():
    app = create_app()

    settings = Settings(
        postgres_user="", postgres_db="", postgres_password="", app_env="test"
    )

    app.dependency_overrides = {get_settings: lambda: settings}

    cliente = TestClient(app=app)

    respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "status": "ok",
        "env": "test",
    }
