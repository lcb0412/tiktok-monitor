"""
数据库连接管理 - SQLite版本
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from core.config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.database.url.replace("sqlite:///", "sqlite+aiosqlite:///"),
    echo=settings.app.debug,
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    from .models import Video, User, VideoHistory, CrawlLog, MonitorTask

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
