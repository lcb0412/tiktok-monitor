"""
URL验证工具
"""

import re
from typing import Optional


TIKTOK_VIDEO_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?tiktok\.com/(?:@[\w.]+)/video/(\d+)"
)
TIKTOK_USER_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?tiktok\.com/@([\w.]+)")


def is_valid_tiktok_url(url: str) -> bool:
    """验证是否为有效的TikTok URL"""
    return bool(TIKTOK_VIDEO_PATTERN.match(url) or TIKTOK_USER_PATTERN.match(url))


def parse_video_id(url: str) -> Optional[str]:
    """从TikTok URL中提取视频ID"""
    match = TIKTOK_VIDEO_PATTERN.search(url)
    if match:
        return match.group(1)
    return None


def parse_user_id(url: str) -> Optional[str]:
    """从TikTok URL中提取用户名"""
    match = TIKTOK_USER_PATTERN.search(url)
    if match:
        return match.group(1)
    return None
