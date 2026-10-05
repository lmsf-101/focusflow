from fastapi import Depends, FastAPI

from focusflow_api.config import Settings, get_settings
from focusflow_api.routers.auth import router as auth_router
from focusflow_api.routers.categories import router as categories_router
from focusflow_api.routers.projects import router as projects_router


def create_app():
    app = FastAPI()

    @app.get("/health")
    def get_health(settings: Settings = Depends(get_settings)):
        return {
            "status": "ok",
            "env": settings.app_env,
        }

    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(categories_router)

    return app
