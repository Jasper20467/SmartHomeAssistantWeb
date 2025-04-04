import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@db:5432/smarthome",
    pool_pre_ping=True,
    echo=True,
    future=True,
    isolation_level="AUTOCOMMIT",  # Add this for asyncpg
    pool_size=5,
    max_overflow=10
)

async def create_tables():
    """Create database tables if they don't exist"""
    try:
        # Add retry logic for database connection
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                async with async_engine.begin() as conn:
                    # Create schedules table
                    await conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS schedules (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            description TEXT,
                            start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                            end_time TIMESTAMP WITH TIME ZONE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    # Create consumables table
                    await conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS consumables (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            category VARCHAR(100) NOT NULL,
                            installation_date DATE NOT NULL,
                            lifetime_days INTEGER NOT NULL,
                            notes TEXT,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                logger.info("Tables created successfully")
                break
            except Exception as e:
                retry_count += 1
                wait_time = 5 * retry_count  # Exponential backoff
                logger.warning(f"Connection attempt {retry_count} failed: {e}. Retrying in {wait_time} seconds...")
                import asyncio
                await asyncio.sleep(wait_time)
        
        if retry_count == max_retries:
            raise Exception("Max retries reached. Could not connect to database.")
            
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
