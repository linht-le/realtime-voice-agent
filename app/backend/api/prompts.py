from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.constants.prompts import INSTRUCTIONS
from app.backend.database.models import Prompt
from app.backend.database.session import get_db
from app.backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class PromptUpdate(BaseModel):
    prompt: str


@router.get("/prompts")
async def get_prompts(db: AsyncSession = Depends(get_db)):
    """Get current prompt (custom if exists, otherwise default from code)"""
    try:
        result = await db.execute(select(Prompt).limit(1))
        active_prompt = result.scalar_one_or_none()
        current = active_prompt.content if active_prompt else INSTRUCTIONS

        return {"current": current, "default": INSTRUCTIONS}
    except Exception as e:
        logger.error(f"Error fetching prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/prompts")
async def update_prompt(data: PromptUpdate, db: AsyncSession = Depends(get_db)):
    """Update or create custom prompt (lazy insert pattern)"""
    try:
        result = await db.execute(select(Prompt).limit(1))
        active_prompt = result.scalar_one_or_none()

        if active_prompt:
            active_prompt.content = data.prompt
        else:
            db.add(Prompt(content=data.prompt))

        await db.commit()
        logger.info("Prompt updated")
        return {"status": "success", "prompt": data.prompt}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/prompts")
async def reset_prompt(db: AsyncSession = Depends(get_db)):
    """Reset prompt to default by deleting custom prompt from DB"""
    try:
        result = await db.execute(select(Prompt).limit(1))
        active_prompt = result.scalar_one_or_none()

        if active_prompt:
            await db.delete(active_prompt)
            await db.commit()
            logger.info("Prompt reset to default")

        return {"status": "success", "prompt": INSTRUCTIONS}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error resetting prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
