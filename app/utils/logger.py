"""
日志配置模块
- 控制台输出
- 文件输出（logs/ 目录，按天轮转）
- 结构化格式
"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from app.config.settings import settings


def setup_logger(name: str = "AgriDialectAgent") -> logging.Logger:
    """
    配置并返回 logger 实例

    特性:
        - 控制台输出
        - 文件按天滚动
        - 统一格式

    参数:
        name: Logger 名称

    返回:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 日志格式
    formatter = logging.Formatter(
        settings.LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件 handler（按天滚动）
    log_file = os.path.join(settings.LOG_DIR, "agent.log")
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# 全局 logger
logger = setup_logger()
