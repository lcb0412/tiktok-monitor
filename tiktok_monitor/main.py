"""
TikTok监控主程序
"""

import asyncio
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from core.config import settings
from core.logger import logger
from api.server import app
from core.crawler import CrawlerManager
from scheduler.scheduler import Scheduler
from storage.database import init_db


async def main():
    logger.info("Starting TikTok Monitor...")

    await init_db()

    crawler_manager = CrawlerManager(cookie=settings.cookie, proxy=settings.proxy)

    scheduler = Scheduler(crawler_manager)
    await scheduler.start()

    import uvicorn

    uvicorn.run(app, host=settings.app.host, port=settings.app.port)


if __name__ == "__main__":
    asyncio.run(main())
