import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parents[3]))

from app.backend.database.session import engine
from app.backend.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


async def reset_database():
    """Drop entire public schema and recreate it, clearing all tables and alembic version"""
    try:
        logger.warning("Dropping entire public schema...")

        async with engine.begin() as conn:
            await conn.execute(text("DROP SCHEMA public CASCADE;"))
            await conn.execute(text("CREATE SCHEMA public;"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO PUBLIC;"))

        logger.info("Database reset completed")
        logger.info("Run 'make migrate-upgrade' to recreate tables")

    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_database())
