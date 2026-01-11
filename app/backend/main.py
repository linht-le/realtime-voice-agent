from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.backend.api import routers
from app.backend.database.session import (
    close_database_connections,
    test_database_connection,
)
from app.backend.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifecycle"""
    logger.info("Starting AI Personal Assistant")

    await test_database_connection()
    logger.info("Application ready")

    yield

    await close_database_connections()
    logger.info("Shutting down")


app = FastAPI(title="AI Personal Assistant", version="0.1.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


@app.get("/")
async def serve_ui():
    if FRONTEND_DIST.exists():
        html_file = FRONTEND_DIST / "index.html"
        if html_file.exists():
            return FileResponse(html_file)

    return {"message": "AI Personal Assistant is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        await test_database_connection()
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "degraded", "database": "disconnected"}
