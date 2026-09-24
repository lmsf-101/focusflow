from focusflow_api.config import Settings


def test_database_url_uses_configured_host_and_port():
    settings = Settings(
        postgres_user="",
        postgres_password="",
        postgres_db="",
        postgres_host="db",
        postgres_port=5433,
    )

    assert settings.database_url.host == "db"

    assert settings.database_url.port == 5433
