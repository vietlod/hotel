"""
Hotel PMS - Database Module
SQLAlchemy async database setup.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


# Determine if we're using SQLite or PostgreSQL
if settings.database_url.startswith("sqlite"):
    # SQLite for development
    SQLALCHEMY_DATABASE_URL = settings.database_url
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Sync session for SQLite
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
else:
    # PostgreSQL with async
    SQLALCHEMY_DATABASE_URL = settings.database_url.replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    async_engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=settings.database_echo
    )
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async def get_db():
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass
