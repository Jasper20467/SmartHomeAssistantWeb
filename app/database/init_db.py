from sqlalchemy.ext.asyncio import create_async_engine

# ...existing code...

async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@db:5432/smarthome",  # 使用 asyncpg 驅動程式，並連接到 Docker 中的 db 服務
    echo=True,
    future=True,
    isolation_level="AUTOCOMMIT",  # Add this for asyncpg
    pool_size=5,
    max_overflow=10
)

# ...existing code...
