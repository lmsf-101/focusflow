from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="")
    app_env: str = "local"

    postgres_user: str
    postgres_password: str
    postgres_db: str


    @property
    def database_url(self) -> URL:
        return URL.create(
                drivername="postgresql+psycopg",
                username=self.postgres_user,
                password=self.postgres_password,
                host="postgres",
                port=5432,
                database=self.postgres_db,
                )



@lru_cache
def get_settings():
    return Settings()
