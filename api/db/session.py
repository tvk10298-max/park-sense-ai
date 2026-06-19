"""Database session factory — async SQLAlchemy + PostGIS."""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('DB_USER', 'parksense')}:"
    f"{os.getenv('DB_PASSWORD', 'changeme')}@"
    f"{os.getenv('DB_HOST', 'db')}:"
    f"{os.getenv('DB_PORT', '5432')}/"
    f"{os.getenv('DB_NAME', 'parksense')}"
)

engine = create_async_engine(DB_URL, echo=False, pool_size=10, max_overflow=20)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
