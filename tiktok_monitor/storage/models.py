"""
数据库模型 - SQLite版本
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    DateTime,
    Text,
    Boolean,
    Float,
)
from .database import Base


class Video(Base):
    """视频模型"""

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(64), unique=True, index=True, nullable=False)
    desc = Column(Text)
    create_time = Column(BigInteger)
    digg_count = Column(BigInteger, default=0)
    share_count = Column(BigInteger, default=0)
    comment_count = Column(BigInteger, default=0)
    play_count = Column(BigInteger, default=0)
    collect_count = Column(BigInteger, default=0)
    author_id = Column(String(64))
    author_name = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sec_uid = Column(String(128), unique=True, index=True, nullable=False)
    username = Column(String(128), unique=True, index=True)
    nickname = Column(String(256))
    follower_count = Column(BigInteger, default=0)
    following_count = Column(BigInteger, default=0)
    likes_count = Column(BigInteger, default=0)
    video_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VideoHistory(Base):
    """视频数据历史记录"""

    __tablename__ = "video_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(64), index=True, nullable=False)
    digg_count = Column(BigInteger, default=0)
    share_count = Column(BigInteger, default=0)
    comment_count = Column(BigInteger, default=0)
    play_count = Column(BigInteger, default=0)
    collect_count = Column(BigInteger, default=0)
    crawled_at = Column(DateTime, default=datetime.utcnow)


class CrawlLog(Base):
    """爬虫日志"""

    __tablename__ = "crawl_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_type = Column(String(32))
    target_id = Column(String(128))
    status = Column(String(32))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class MonitorTask(Base):
    """监控任务"""

    __tablename__ = "monitor_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(32), nullable=False)
    target_id = Column(String(128), nullable=False)
    name = Column(String(256))
    interval = Column(Integer, default=300)
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime)
    last_status = Column(String(32))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
