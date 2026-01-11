from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.database.models import Tool
from app.backend.database.session import get_db
from app.backend.logger import get_logger
from app.backend.services.tool_service import TOOL_GROUPS

logger = get_logger(__name__)
router = APIRouter()


class ToolToggle(BaseModel):
    name: str
    enabled: bool


class ToolUpdate(BaseModel):
    name: str
    description: str


@router.get("/tools")
async def get_tools(db: AsyncSession = Depends(get_db)):
    """Get all available tools with their enabled status"""
    try:
        result = await db.execute(select(Tool))
        db_tools = {t.name: t for t in result.scalars().all()}

        tools = []
        for name in TOOL_GROUPS:
            tool = db_tools.get(name)
            tools.append({
                "id": tool.id if tool else None,
                "name": name,
                "enabled": tool.enabled if tool else True,
                "description": (
                    tool.description if tool and tool.description
                    else TOOL_GROUPS[name]["description"]
                ),
                "created_at": tool.created_at.isoformat() if tool else None,
                "updated_at": tool.updated_at.isoformat() if tool else None,
            })
        return tools
    except Exception as e:
        logger.error(f"Failed to fetch tools: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tools") from e


@router.post("/tools/toggle")
async def toggle_tool(toggle_data: ToolToggle, db: AsyncSession = Depends(get_db)):
    """Toggle tool on/off"""
    try:
        if toggle_data.name not in TOOL_GROUPS:
            raise HTTPException(status_code=404, detail=f"Tool '{toggle_data.name}' not found")

        result = await db.execute(select(Tool).where(Tool.name == toggle_data.name))
        tool = result.scalar_one_or_none()

        if tool:
            tool.enabled = toggle_data.enabled
        else:
            tool = Tool(name=toggle_data.name, enabled=toggle_data.enabled)
            db.add(tool)

        await db.commit()
        await db.refresh(tool)

        logger.info(f"Tool '{toggle_data.name}' {'enabled' if toggle_data.enabled else 'disabled'}")
        return {"id": tool.id, "name": tool.name, "enabled": tool.enabled}
    except Exception as e:
        logger.error(f"Failed to toggle tool: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle tool") from e


@router.put("/tools/description")
async def update_tool_description(update_data: ToolUpdate, db: AsyncSession = Depends(get_db)):
    """Update tool description"""
    try:
        if update_data.name not in TOOL_GROUPS:
            raise HTTPException(status_code=404, detail=f"Tool '{update_data.name}' not found")

        result = await db.execute(select(Tool).where(Tool.name == update_data.name))
        tool = result.scalar_one_or_none()

        if tool:
            tool.description = update_data.description
        else:
            tool = Tool(name=update_data.name, description=update_data.description)
            db.add(tool)

        await db.commit()
        await db.refresh(tool)

        logger.info(f"Tool '{update_data.name}' description updated")
        return {"id": tool.id, "name": tool.name, "description": tool.description}
    except Exception as e:
        logger.error(f"Failed to update tool description: {e}")
        raise HTTPException(status_code=500, detail="Failed to update tool description") from e


@router.delete("/tools/description/{tool_name}")
async def reset_tool_description(tool_name: str, db: AsyncSession = Depends(get_db)):
    """Reset tool description to default"""
    try:
        if tool_name not in TOOL_GROUPS:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        result = await db.execute(select(Tool).where(Tool.name == tool_name))
        tool = result.scalar_one_or_none()

        if tool:
            tool.description = None
            await db.commit()
            await db.refresh(tool)

        logger.info(f"Tool '{tool_name}' description reset to default")
        return {
            "id": tool.id if tool else None,
            "name": tool_name,
            "description": TOOL_GROUPS[tool_name]["description"],
        }
    except Exception as e:
        logger.error(f"Failed to reset tool description: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset tool description") from e
