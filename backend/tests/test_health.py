from fastapi.testclient import TestClient

from focusflow_api.app import create_app
from focusflow_api.config import Settings, get_settings


def test_health_returns_ok():
    app = create_app()

    settings = Settings(
        postgres_user="",
        postgres_db="",
        postgres_password="",
        app_env="test",
        render_git_commit="test",
    )

    app.dependency_overrides = {get_settings: lambda: settings}

    client = TestClient(app=app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "env": "test",
        "render_git_commit": "test",
    }


def test_health_commit_is_null_when_env_is_missing(monkeypatch):
    app = create_app()

    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)

    settings = Settings(
        postgres_user="",
        postgres_db="",
        postgres_password="",
        app_env="test",
    )

    app.dependency_overrides = {get_settings: lambda: settings}

    client = TestClient(app=app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["render_git_commit"] is None
