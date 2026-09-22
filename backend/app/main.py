from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes import router
from backend.app.core.config import settings
from backend.app.core.paths import repo_root
from backend.app.services.bootstrap import ensure_demo_ready


def _dist_dir() -> Path:
    return repo_root() / "frontend" / "dist"


def _cors_origins() -> list[str]:
    return [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_demo_ready()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.9.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api")

    @app.get("/health")
    def health() -> dict[str, str | int]:
        return {
            "status": "ok",
            "service": settings.app_name,
            "product": "revenueops-control-tower",
            "autonomy_mode": settings.autonomy_mode,
            "host": settings.host,
            "port": settings.port,
        }

    dist = _dist_dir()
    index = dist / "index.html"
    assets = dist / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/", include_in_schema=False)
    def root():
        if index.is_file():
            return FileResponse(index)
        return {
            "status": "ok",
            "service": settings.app_name,
            "product": "revenueops-control-tower",
            "ui": "not-built",
            "hint": "Run bash scripts/serve.sh, or start the Vite dev server on port 3066.",
        }

    if index.is_file():

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa(full_path: str) -> FileResponse:
            if full_path == "api" or full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not found")
            candidate = (dist / full_path).resolve()
            try:
                candidate.relative_to(dist.resolve())
            except ValueError:
                return FileResponse(index)
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(index)

    return app


app = create_app()
