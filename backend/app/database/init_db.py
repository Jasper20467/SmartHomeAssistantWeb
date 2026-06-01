import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/smarthome"
)

async_engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True,
    future=True,
    isolation_level="AUTOCOMMIT",  # Add this for asyncpg
    pool_size=5,
    max_overflow=10
)

async def verify_connection():
    """Verify database connectivity. Schema is managed by external infra."""
    import asyncio
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection verified")
            return
        except Exception as e:
            retry_count += 1
            wait_time = 5 * retry_count
            logger.warning(f"Connection attempt {retry_count} failed: {e}. Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)

    raise Exception("Max retries reached. Could not connect to database.")
