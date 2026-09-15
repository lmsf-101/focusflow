from fastapi import Depends, FastAPI

from focusflow_api.config import Settings, get_settings


def create_app():
    app = FastAPI()

    @app.get("/health")
    def get_health(settings: Settings = Depends(get_settings)):
        return {
            "status": "ok",
            "env": settings.app_env,
        }

    return app
