"""
定时任务调度器
"""

import asyncio
from datetime import datetime
from typing import List, Optional
from core.logger import logger
from storage.database import async_session_maker
from storage.repositories import MonitorTaskRepository


class Scheduler:
    def __init__(self, crawler_manager):
        self.crawler = crawler_manager
        self.running = False
        self.tasks = {}

    async def start(self):
        """启动调度器"""
        self.running = True
        logger.info("Scheduler started")
        await self._run_tasks()

    async def stop(self):
        """停止调度器"""
        self.running = False
        logger.info("Scheduler stopped")

    async def _run_tasks(self):
        """运行所有监控任务"""
        while self.running:
            try:
                async with async_session_maker() as db:
                    task_repo = MonitorTaskRepository()
                    active_tasks = await task_repo.get_active_tasks(db)
                    for task in active_tasks:
                        task_id = task.id
                        if task_id not in self.tasks or not self.tasks[task_id].done():
                            self.tasks[task_id] = asyncio.create_task(
                                self._execute_task(task)
                            )
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            await asyncio.sleep(60)

    async def _execute_task(self, task):
        """执行单个监控任务"""
        try:
            async with async_session_maker() as db:
                task_repo = MonitorTaskRepository()
                if task.task_type == "video":
                    await self.crawler.crawl_video(task.target_id)
                elif task.task_type == "user":
                    await self.crawler.crawl_user(task.target_id)
                elif task.task_type == "user_videos":
                    await self.crawler.crawl_user_videos(task.target_id)

                await task_repo.update_last_run(db, task.id, success=True)
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            try:
                async with async_session_maker() as db:
                    task_repo = MonitorTaskRepository()
                    await task_repo.update_last_run(db, task.id, success=False)
            except:
                pass
