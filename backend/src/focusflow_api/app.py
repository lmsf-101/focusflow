import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from focusflow_api.config import Settings, get_settings
from focusflow_api.logging import configure_logging
from focusflow_api.routers.auth import router as auth_router
from focusflow_api.routers.categories import router as categories_router
from focusflow_api.routers.projects import router as projects_router
from focusflow_api.routers.tags import router as tags_router
from focusflow_api.routers.tasks import router as tasks_router


def create_app():
    app = FastAPI()

    configure_logging()
    log = structlog.get_logger()

    @app.middleware("http")
    async def add_request_id_middleware(
        request: Request, call_next: Callable
    ) -> Response:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=str(uuid.uuid4()))

        request_time_init = time.perf_counter()
        status_code = 500
        try:
            response: Response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            request_time_end = time.perf_counter()
            log.info(
                "request completed",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=(round((request_time_end - request_time_init) * 1000)),
            )

    @app.get("/health")
    def get_health(settings: Settings = Depends(get_settings)):
        log.info("health_checked")
        return {
            "status": "ok",
            "env": settings.app_env,
            "render_git_commit": settings.render_git_commit,
        }

    app.add_middleware(
        CORSMiddleware,
        allow_methods=["*"],
        allow_headers=["Authorization"],
        allow_origins=get_settings().cors_origins,
    )

    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(categories_router)
    app.include_router(tasks_router)
    app.include_router(tags_router)

    log.info("app started")

    return app
