"""
数据访问层
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Video, User, VideoHistory, CrawlLog, MonitorTask


class BaseRepository:
    """基础仓储类"""

    def __init__(self, model):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: int):
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, limit: int = 100, offset: int = 0):
        result = await db.execute(select(self.model).limit(limit).offset(offset))
        return result.scalars().all()

    async def delete(self, db: AsyncSession, id: int):
        await db.execute(delete(self.model).where(self.model.id == id))
        await db.commit()


class VideoRepository(BaseRepository):
    """视频仓储"""

    def __init__(self):
        super().__init__(Video)

    async def get_by_video_id(self, db: AsyncSession, video_id: str):
        result = await db.execute(select(Video).where(Video.video_id == video_id))
        return result.scalar_one_or_none()

    async def create_or_update(self, db: AsyncSession, video_id: str, data: dict):
        existing = await self.get_by_video_id(db, video_id)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
        else:
            video = Video(video_id=video_id, **data)
            db.add(video)
        await db.commit()

    async def get_videos_by_author(self, db: AsyncSession, author_id: str):
        result = await db.execute(select(Video).where(Video.author_id == author_id))
        return result.scalars().all()

    async def get_top_videos(self, db: AsyncSession, limit: int = 10):
        result = await db.execute(
            select(Video).order_by(Video.play_count.desc()).limit(limit)
        )
        return result.scalars().all()


class UserRepository(BaseRepository):
    """用户仓储"""

    def __init__(self):
        super().__init__(User)

    async def get_by_sec_uid(self, db: AsyncSession, sec_uid: str):
        result = await db.execute(select(User).where(User.sec_uid == sec_uid))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str):
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create_or_update(self, db: AsyncSession, sec_uid: str, data: dict):
        existing = await self.get_by_sec_uid(db, sec_uid)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
        else:
            user = User(sec_uid=sec_uid, **data)
            db.add(user)
        await db.commit()


class VideoHistoryRepository(BaseRepository):
    """视频历史数据仓储"""

    def __init__(self):
        super().__init__(VideoHistory)

    async def add_history(self, db: AsyncSession, video_id: str, data: dict):
        history = VideoHistory(video_id=video_id, **data)
        db.add(history)
        await db.commit()

    async def get_history(self, db: AsyncSession, video_id: str, limit: int = 100):
        result = await db.execute(
            select(VideoHistory)
            .where(VideoHistory.video_id == video_id)
            .order_by(VideoHistory.crawled_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


class CrawlLogRepository(BaseRepository):
    """爬虫日志仓储"""

    def __init__(self):
        super().__init__(CrawlLog)

    async def add_log(
        self,
        db: AsyncSession,
        target_type: str,
        target_id: str,
        status: str,
        message: str = "",
    ):
        log = CrawlLog(
            target_type=target_type, target_id=target_id, status=status, message=message
        )
        db.add(log)
        await db.commit()

    async def get_recent_logs(self, db: AsyncSession, limit: int = 100):
        result = await db.execute(
            select(CrawlLog).order_by(CrawlLog.created_at.desc()).limit(limit)
        )
        return result.scalars().all()


class MonitorTaskRepository(BaseRepository):
    """监控任务仓储"""

    def __init__(self):
        super().__init__(MonitorTask)

    async def get_active_tasks(self, db: AsyncSession):
        result = await db.execute(
            select(MonitorTask).where(MonitorTask.enabled == True)
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        task_type: str,
        target_id: str,
        name: str = None,
        interval: int = 300,
    ):
        task = MonitorTask(
            task_type=task_type,
            target_id=target_id,
            name=name or target_id,
            interval=interval,
        )
        db.add(task)
        await db.commit()
        return task

    async def update_last_run(self, db: AsyncSession, task_id: int, success: bool):
        await db.execute(
            update(MonitorTask)
            .where(MonitorTask.id == task_id)
            .values(
                last_run=datetime.utcnow(),
                last_status="success" if success else "failed",
            )
        )
        await db.commit()
