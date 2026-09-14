from pydantic.networks import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="")
    app_env: str = "local"

@lru_cache
def get_settings():
    return Settings()

