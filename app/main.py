import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting LangGraph Voice Agent Server")
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set in environment")
    if not settings.TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY not set for search functionality")

    yield

    logger.info("Shutting down LangGraph Voice Agent Server")


app = FastAPI(title="LangGraph Voice Agent", version="0.1.0", lifespan=lifespan)

# Include API routes
app.include_router(router)

# Setup static files directory
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Serve HTML UI at root
@app.get("/")
async def serve_ui():
    """Serve the voice assistant UI"""
    html_file = STATIC_DIR / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Voice Agent API is running. Upload UI to /app/static/index.html"}


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    favicon_file = STATIC_DIR / "favicon.ico"
    if favicon_file.exists():
        return FileResponse(favicon_file)
    return Response(status_code=204)
