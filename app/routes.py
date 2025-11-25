import asyncio
import logging
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile, WebSocket

from app.agent.agent import VoiceAgent
from app.agent.prompt import INSTRUCTIONS
from app.agent.tools import get_document_query_tool, get_search_tools
from app.config import get_settings
from app.rag.ingestion import ingest_document

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    settings = get_settings()

    # Combine search tools and RAG tool
    all_tools = [*get_search_tools(), get_document_query_tool()]
    logger.info(f"Loaded {len(all_tools)} tools: {[t.name for t in all_tools]}")

    agent = VoiceAgent(
        model=settings.OPENAI_MODEL_NAME,
        voice=settings.VOICE,
        instructions=INSTRUCTIONS,
        tools=all_tools,
        api_key=settings.OPENAI_API_KEY,
    )

    try:
        await agent.connect()

        async def handle_browser():
            while True:
                try:
                    message = await websocket.receive_text()
                    await agent.handle_browser_message(message)
                except Exception:
                    break

        async def handle_openai():
            await agent.process_openai_events(lambda msg: websocket.send_text(msg))

        await asyncio.gather(handle_browser(), handle_openai())

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        await agent.disconnect()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and ingest document into Qdrant"""
    try:
        if not file.filename or not file.filename.endswith(".docx"):
            raise HTTPException(status_code=400, detail="Only DOCX files supported")

        with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
            tmp.write(await file.read())
            tmp.flush()
            ingest_document(tmp.name)

        logger.info(f"Ingested: {file.filename}")
        return {"status": "success", "filename": file.filename}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
