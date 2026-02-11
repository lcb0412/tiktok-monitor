"""
日志配置模块
"""

from loguru import logger
from loguru._defaults import LOGURU_FORMAT


def setup_logging(
    level: str = "INFO", log_file: str = "logs/app.log", console: bool = True
) -> None:
    """配置日志系统"""
    logger.remove()

    log_path = log_file
    log_dir = (
        log_path.rsplit("/", 1)[0] if "/" in log_path else log_path.rsplit("\\", 1)[0]
    )
    import os

    os.makedirs(log_dir, exist_ok=True)

    if console:
        logger.add(
            sink=lambda msg: print(msg, end=""),
            format=LOGURU_FORMAT,
            level=level.upper(),
            colorize=True,
        )

    logger.add(
        sink=log_file,
        format=LOGURU_FORMAT,
        level=level.upper(),
        encoding="utf-8",
        enqueue=True,
    )


def get_logger(name: str = None):
    """获取日志记录器"""
    return logger.bind(name=name)


def configure_default_logging(config) -> None:
    """根据配置默认日志系统"""
    setup_logging(
        level=config.logging.level,
        log_file=config.logging.file,
        console=config.logging.console,
    )
