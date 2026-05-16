"""
Database configuration and session management.
Supports both SQLite (development) and PostgreSQL (production).
"""
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker


from sqlalchemy.ext.asyncio.engine import AsyncEngine


from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings

# Create async engine
engine: AsyncEngine = create_async_engine(
    url=settings.database_url,
    echo=settings.database_echo,
    future=True,
)

# Create async session factory
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in SQLAlchemy models.
    
    Note:
        In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Drop all database tables.
    
    Warning:
        This will delete all data! Use only in development/testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db() -> None:
    """
    Close database connections.
    Should be called on application shutdown.
    """
    await engine.dispose()

# Made with Bob
