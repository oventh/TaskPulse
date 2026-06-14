"""FastAPI application entry point."""

import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.agents import router as agents_router
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.executions import router as executions_router
from app.api.notifications import router as notifications_router
from app.api.dashboard import router as dashboard_router
from app.api.system import router as system_router
from app.config import settings
from app.database import engine, Base, async_session_factory
from app.services.scheduler import SchedulerService
from app.services.auth import AuthService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("taskpulse")

scheduler = SchedulerService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables + start background scheduler."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured")
    # Ensure default admin
    async with async_session_factory() as db:
        await AuthService.ensure_default_admin(db)
    # Start background scheduler
    task = asyncio.create_task(scheduler.start())
    yield
    # Shutdown
    await scheduler.stop()
    task.cancel()
    await engine.dispose()


app = FastAPI(
    title="TaskPulse — AI Agent Task Monitor",
    description="Unified dashboard for tracking, monitoring and alerting on AI agent scheduled tasks.",
    version="1.0.0",
    lifespan=lifespan,
)

# API routers
app.include_router(agents_router)
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(executions_router)
app.include_router(notifications_router)
app.include_router(dashboard_router)
app.include_router(system_router)


# Serve Vue3 static files (SPA — monolithic deployment)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    # Mount assets directory for JS/CSS/fonts
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.exception_handler(404)
    async def spa_fallback(request: Request, exc):
        """Return index.html for any non-API route (Vue Router SPA)."""
        if not request.url.path.startswith("/api"):
            content = (FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
            return HTMLResponse(content=content, status_code=200)
        raise exc

    logger.info("Frontend SPA mounted from %s", FRONTEND_DIST)
else:
    logger.info("Frontend dist not found at %s — API-only mode", FRONTEND_DIST)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "taskpulse"}
