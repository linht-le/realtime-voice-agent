import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.database.models import Settings
from app.backend.database.session import get_db
from app.backend.logger import get_logger
from app.backend.services.settings_service import SettingsService

logger = get_logger(__name__)
router = APIRouter()


class SettingsUpdate(BaseModel):
    backend: dict = {}
    client: dict = {}


@router.get("/settings")
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Get settings merged with defaults"""
    try:
        default_schema = SettingsService.load_default_settings()
        result = await db.execute(select(Settings).limit(1))
        record = result.scalar_one_or_none()

        if record:
            try:
                custom_backend = json.loads(record.backend_settings)
                custom_client = json.loads(record.client_settings)
                backend = SettingsService.merge_settings(
                    default_schema.get("backend", {}), custom_backend
                )
                client = SettingsService.merge_settings(
                    default_schema.get("client", {}), custom_client
                )
            except json.JSONDecodeError as e:
                logger.error(f"Corrupted settings JSON: {e}")
                raise HTTPException(status_code=500, detail="Settings data is corrupted") from e
        else:
            backend = default_schema.get("backend", {})
            client = default_schema.get("client", {})

        return {
            "backend": SettingsService.ensure_value_field(backend),
            "client": SettingsService.ensure_value_field(client),
        }

    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch settings") from e


@router.put("/settings")
async def update_settings(updates: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    """Update settings"""
    try:
        default_schema = SettingsService.load_default_settings()
        result = await db.execute(select(Settings).limit(1))
        record = result.scalar_one_or_none()

        if record:
            try:
                existing_backend = json.loads(record.backend_settings)
                existing_client = json.loads(record.client_settings)
            except json.JSONDecodeError as e:
                logger.error(f"Corrupted settings JSON: {e}")
                raise HTTPException(status_code=500, detail="Settings data is corrupted") from e

            merged_backend_data = {**existing_backend, **updates.backend}
            merged_client_data = {**existing_client, **updates.client}
            merged_backend = SettingsService.merge_settings(
                default_schema.get("backend", {}), merged_backend_data
            )
            merged_client = SettingsService.merge_settings(
                default_schema.get("client", {}), merged_client_data
            )

            record.backend_settings = json.dumps(
                updates.backend if updates.backend else existing_backend
            )
            record.client_settings = json.dumps(
                updates.client if updates.client else existing_client
            )
        else:
            merged_backend = SettingsService.merge_settings(
                default_schema.get("backend", {}), updates.backend
            )
            merged_client = SettingsService.merge_settings(
                default_schema.get("client", {}), updates.client
            )

            record = Settings(
                backend_settings=json.dumps(updates.backend),
                client_settings=json.dumps(updates.client),
            )
            db.add(record)

        await db.commit()
        await db.refresh(record)

        logger.info("Settings updated")
        return {
            "backend": SettingsService.ensure_value_field(merged_backend),
            "client": SettingsService.ensure_value_field(merged_client),
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings") from e


@router.delete("/settings")
async def reset_settings(db: AsyncSession = Depends(get_db)):
    """Reset settings to defaults"""
    try:
        result = await db.execute(select(Settings).limit(1))
        record = result.scalar_one_or_none()

        if record:
            await db.delete(record)
            await db.commit()
            logger.info("Settings reset to defaults")

        default_schema = SettingsService.load_default_settings()
        return {
            "backend": SettingsService.ensure_value_field(default_schema.get("backend", {})),
            "client": SettingsService.ensure_value_field(default_schema.get("client", {})),
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Error resetting settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset settings") from e
