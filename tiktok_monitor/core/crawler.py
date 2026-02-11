"""
TikTok 爬虫引擎
"""

import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode, urlparse
from .signer import XBogusSigner
from .logger import logger
from storage.repositories import VideoRepository, UserRepository


class TikTokCrawler:
    def __init__(self, cookie: str = None, proxy: str = None):
        self.cookie = cookie or ""
        self.proxy = proxy
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.tiktok.com/",
        }
        if self.cookie:
            self.headers["Cookie"] = self.cookie
        self.signer = XBogusSigner(self.headers["User-Agent"])

    async def _make_request(
        self, url: str, params: Dict = None, need_sign: bool = True
    ) -> Optional[Dict[str, Any]]:
        """发起HTTP请求"""
        try:
            if need_sign and "web.tiktok.com" in url:
                if params:
                    signed_url = self.signer.get_xbogus(f"{url}?{urlencode(params)}")[0]
                else:
                    signed_url = self.signer.get_xbogus(url)[0]
                parsed = urlparse(signed_url)
                url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                params = dict(parsed.query)

            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(
                connector=connector,
                headers=self.headers,
            ) as session:
                async with session.get(
                    url, params=params, proxy=self.proxy
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(
                            f"Request failed with status {response.status}: {url}"
                        )
                        return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    async def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """获取视频详情"""
        url = "https://www.tiktok.com/api/item/detail/"
        params = {"item_id": video_id}
        data = await self._make_request(url, params)
        if data and "item_info" in data:
            return data["item_info"]
        return None

    async def get_user_info(self, sec_uid: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        url = "https://www.tiktok.com/api/user/detail/"
        params = {"sec_user_id": sec_uid}
        data = await self._make_request(url, params)
        if data and "user_info" in data:
            return data["user_info"]
        return None

    async def get_user_videos(
        self, sec_uid: str, count: int = 30, cursor: int = 0
    ) -> Optional[Dict[str, Any]]:
        """获取用户视频列表"""
        url = "https://www.tiktok.com/api/post/item_list/"
        params = {
            "sec_user_id": sec_uid,
            "count": count,
            "cursor": cursor,
        }
        return await self._make_request(url, params)

    async def extract_video_id(self, share_url: str) -> Optional[str]:
        """从分享链接提取视频ID"""
        if "vt.tiktok.com" in share_url or "vm.tiktok.com" in share_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    share_url, allow_redirects=True, proxy=self.proxy
                ) as response:
                    share_url = str(response.url)
        if "/video/" in share_url:
            parts = share_url.split("/video/")
            if len(parts) > 1:
                video_id = parts[1].split("?")[0].split("/")[0]
                return video_id
        return None

    async def extract_sec_uid(self, share_url: str) -> Optional[str]:
        """从分享链接提取用户sec_uid"""
        if "tiktok.com@" in share_url or "@" in share_url:
            parts = share_url.split("@")
            if len(parts) > 1:
                username = parts[1].split("/")[0]
                user_info = await self.get_user_info_by_username(username)
                if user_info:
                    return user_info.get("sec_uid")
        return None

    async def get_user_info_by_username(
        self, username: str
    ) -> Optional[Dict[str, Any]]:
        """通过用户名获取用户信息"""
        url = "https://www.tiktok.com/api/user/detail/"
        params = {"unique_id": username}
        data = await self._make_request(url, params)
        if data and "user_info" in data:
            return data["user_info"]
        return None


class CrawlerManager:
    def __init__(self, cookie: str = None, proxy: str = None):
        self.crawler = TikTokCrawler(cookie, proxy)
        self.video_repo = VideoRepository()
        self.user_repo = UserRepository()

    async def crawl_video(self, video_id: str) -> bool:
        """爬取单个视频数据"""
        video_info = await self.crawler.get_video_info(video_id)
        if not video_info:
            logger.error(f"Failed to get video info: {video_id}")
            return False

        data = {
            "video_id": video_id,
            "desc": video_info.get("desc", ""),
            "create_time": video_info.get("create_time", 0),
            "digg_count": video_info.get("digg_count", 0),
            "share_count": video_info.get("share_count", 0),
            "comment_count": video_info.get("comment_count", 0),
            "play_count": video_info.get("play_count", 0),
            "collect_count": video_info.get("collect_count", 0),
            "author_id": video_info.get("author_id", ""),
            "author_name": video_info.get("author", ""),
        }

        await self.video_repo.create_or_update(video_id, data)
        logger.info(f"Crawled video: {video_id}")
        return True

    async def crawl_user(self, sec_uid: str) -> bool:
        """爬取单个用户数据"""
        user_info = await self.crawler.get_user_info(sec_uid)
        if not user_info:
            logger.error(f"Failed to get user info: {sec_uid}")
            return False

        data = {
            "sec_uid": sec_uid,
            "username": user_info.get("unique_id", ""),
            "nickname": user_info.get("nickname", ""),
            "follower_count": user_info.get("follower_count", 0),
            "following_count": user_info.get("following_count", 0),
            "likes_count": user_info.get("likes_count", 0),
            "video_count": user_info.get("video_count", 0),
        }

        await self.user_repo.create_or_update(sec_uid, data)
        logger.info(f"Crawled user: {sec_uid}")
        return True

    async def crawl_user_videos(self, sec_uid: str, max_videos: int = 100) -> int:
        """爬取用户所有视频数据"""
        cursor = 0
        total_crawled = 0

        while total_crawled < max_videos:
            result = await self.crawler.get_user_videos(
                sec_uid, count=30, cursor=cursor
            )
            if not result or "items" not in result:
                break

            for item in result["items"]:
                video_id = item.get("id")
                if video_id:
                    data = {
                        "video_id": video_id,
                        "desc": item.get("desc", ""),
                        "create_time": item.get("create_time", 0),
                        "digg_count": item.get("digg_count", 0),
                        "share_count": item.get("share_count", 0),
                        "comment_count": item.get("comment_count", 0),
                        "play_count": item.get("play_count", 0),
                        "collect_count": item.get("collect_count", 0),
                        "author_id": item.get("author_id", ""),
                    }
                    await self.video_repo.create_or_update(video_id, data)
                    total_crawled += 1

            if "cursor" in result:
                cursor = result["cursor"]
                if not result.get("has_more", False):
                    break
            else:
                break

        logger.info(f"Crawled {total_crawled} videos for user: {sec_uid}")
        return total_crawled
