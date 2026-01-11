import asyncio
import contextlib
import json

from fastapi import APIRouter, WebSocket
from sqlalchemy import select
from starlette.websockets import WebSocketDisconnect

from app.backend.config import get_settings
from app.backend.constants.prompts import INSTRUCTIONS
from app.backend.database.models import Prompt, Settings
from app.backend.database.session import AsyncSessionLocal
from app.backend.logger import get_logger
from app.backend.services.settings_service import SettingsService
from app.backend.services.tool_service import ToolService
from app.backend.services.voice.agent import VoiceAgent

logger = get_logger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for voice agent"""
    await websocket.accept()
    settings = get_settings()

    user_settings, instructions, active_prompt = await _load_session_config()
    all_tools = await ToolService.get_all_tools()
    prompt_type = "custom" if active_prompt else "default"
    logger.info(f"New session started (prompt={prompt_type}, {len(all_tools)} tools)")

    agent = VoiceAgent(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY,
        user_settings=user_settings,
        instructions=instructions,
        tools=all_tools,
    )

    try:
        await agent.connect()

        async def handle_browser():
            try:
                while True:
                    message = await websocket.receive_text()
                    await agent.handle_browser_message(message)
            except WebSocketDisconnect:
                logger.info("Browser disconnected")
            except Exception as e:
                logger.error(f"Browser handler error: {type(e).__name__}: {e}")

        async def handle_openai():
            await agent.process_openai_events(lambda msg: websocket.send_text(msg))

        browser_task = asyncio.create_task(handle_browser())
        openai_task = asyncio.create_task(handle_openai())

        _, pending = await asyncio.wait(
            [browser_task, openai_task], return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        logger.info("Session ended")

    except Exception as e:
        logger.error(f"Session error: {type(e).__name__}: {e}", exc_info=True)
    finally:
        await agent.disconnect()
        with contextlib.suppress(Exception):
            await websocket.close()


async def _load_session_config() -> tuple[dict, str, Prompt | None]:
    """Load settings and prompt from database"""
    async with AsyncSessionLocal() as db:
        default_schema = SettingsService.load_default_settings()

        settings_result = await db.execute(select(Settings).limit(1))
        custom_settings = settings_result.scalar_one_or_none()

        if custom_settings:
            custom_backend = json.loads(custom_settings.backend_settings)
            custom_client = json.loads(custom_settings.client_settings)
            backend = SettingsService.merge_settings(
                default_schema.get("backend", {}), custom_backend
            )
            client = SettingsService.merge_settings(
                default_schema.get("client", {}), custom_client
            )
        else:
            backend = default_schema.get("backend", {})
            client = default_schema.get("client", {})

        user_settings = {"backend": backend, "client": client}

        prompt_result = await db.execute(select(Prompt).limit(1))
        active_prompt = prompt_result.scalar_one_or_none()
        instructions = active_prompt.content if active_prompt else INSTRUCTIONS

        return user_settings, instructions, active_prompt
