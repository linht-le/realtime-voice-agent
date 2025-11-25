import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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

app.include_router(router)
