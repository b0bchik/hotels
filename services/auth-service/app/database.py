from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from .config import settings

from typing import AsyncGenerator


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_connection() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as connection:
        yield connection
