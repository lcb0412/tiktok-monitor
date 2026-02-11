"""
配置加载模块 - SQLite版本
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """数据库配置 - SQLite"""

    path: str = "data/tiktok_monitor.db"
    table_prefix: str = ""

    @property
    def url(self) -> str:
        """生成数据库URL"""
        return f"sqlite:///{self.path}"


class RedisConfig(BaseModel):
    """Redis配置"""

    enabled: bool = False
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None


class AppConfig(BaseModel):
    """应用配置"""

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 1
    secret_key: str = "change-me-in-production"


class TikTokCrawlerConfig(BaseModel):
    """TikTok爬虫配置"""

    user_agents: List[str] = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)
    request_interval: float = 1.0
    max_retries: int = 3
    timeout: int = 30
    concurrency: int = 5


class CrawlerConfig(BaseModel):
    """爬虫配置"""

    request_interval: float = 1.0
    max_retries: int = 3
    timeout: int = 30
    concurrency: int = 5
    tiktok: TikTokCrawlerConfig = Field(default_factory=TikTokCrawlerConfig)


class MonitoringConfig(BaseModel):
    """监控配置"""

    enabled: bool = True
    default_interval: int = 300
    data_retention_days: int = 30


class SchedulerConfig(BaseModel):
    """定时任务配置"""

    enabled: bool = True
    timezone: str = "Asia/Shanghai"


class LoggingConfig(BaseModel):
    """日志配置"""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/app.log"
    console: bool = True


class Config(BaseModel):
    """主配置类"""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    crawler: CrawlerConfig = Field(default_factory=CrawlerConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_path: Optional[str] = None) -> Config:
    """加载配置文件"""
    if config_path is None:
        config_path = os.environ.get(
            "TIKTOK_MONITOR_CONFIG", str(Path(__file__).parent / "config.yaml")
        )

    config_file = Path(config_path)

    if not config_file.exists():
        config_data = {}
    else:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}

    return Config(**config_data)


_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: Config) -> None:
    """设置全局配置实例"""
    global _config
    _config = config


settings = get_config()
