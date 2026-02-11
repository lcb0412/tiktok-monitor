"""
FastAPI 服务器
"""

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from storage.database import get_db, init_db
from storage.repositories import (
    VideoRepository,
    UserRepository,
    MonitorTaskRepository,
)
from core.crawler import CrawlerManager
from core.config import settings

app = FastAPI(
    title="TikTok Monitor API", description="TikTok数据监控API", version="1.0.0"
)


@app.on_event("startup")
async def startup():
    await init_db()


video_repo = VideoRepository()
user_repo = UserRepository()
task_repo = MonitorTaskRepository()


@app.get("/")
async def root():
    return {"message": "TikTok Monitor API", "docs": "/docs"}


@app.get("/api/videos")
async def get_videos(
    limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    videos = await video_repo.get_all(db, limit=limit, offset=offset)
    return {"videos": videos}


@app.get("/api/videos/{video_id}")
async def get_video(video_id: str, db: AsyncSession = Depends(get_db)):
    video = await video_repo.get_by_video_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@app.get("/api/videos/top")
async def get_top_videos(limit: int = 10, db: AsyncSession = Depends(get_db)):
    videos = await video_repo.get_top_videos(db, limit=limit)
    return {"videos": videos}


@app.get("/api/users")
async def get_users(
    limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    users = await user_repo.get_all(db, limit=limit, offset=offset)
    return {"users": users}


@app.get("/api/users/{sec_uid}")
async def get_user(sec_uid: str, db: AsyncSession = Depends(get_db)):
    user = await user_repo.get_by_sec_uid(db, sec_uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/api/tasks")
async def get_tasks(db: AsyncSession = Depends(get_db)):
    tasks = await task_repo.get_active_tasks(db)
    return {"tasks": tasks}


@app.post("/api/crawl/video")
async def crawl_video(video_id: str, db: AsyncSession = Depends(get_db)):
    crawler = CrawlerManager()
    success = await crawler.crawl_video(video_id)
    return {"success": success, "video_id": video_id}


@app.post("/api/crawl/user")
async def crawl_user(sec_uid: str, db: AsyncSession = Depends(get_db)):
    crawler = CrawlerManager()
    success = await crawler.crawl_user(sec_uid)
    return {"success": success, "sec_uid": sec_uid}


@app.post("/api/tasks")
async def create_task(
    task_type: str,
    target_id: str,
    name: Optional[str] = None,
    interval: int = 300,
    db: AsyncSession = Depends(get_db),
):
    task = await task_repo.create(db, task_type, target_id, name, interval)
    return {"task": task}
