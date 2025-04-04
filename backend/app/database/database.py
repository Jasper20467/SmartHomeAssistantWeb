import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql+asyncpg://postgres:postgres@db:5432/smarthome"
# )

# Configure async engine with correct asyncpg settings
async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@db:5432/smarthome",
    echo=True,
    future=True,
    isolation_level="AUTOCOMMIT",  # Add this for asyncpg
    pool_size=5,
    max_overflow=10
)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
