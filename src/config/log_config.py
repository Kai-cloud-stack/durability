#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志配置文件
集中管理整个项目的日志配置
"""

import logging
import logging.config
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 日志目录
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志配置字典
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d]: %(message)s"
        }
    },
    
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(LOG_DIR / "app.log"),
            "maxBytes": 300 * 1024 * 1024,  # 修改为300MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "file_can": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(LOG_DIR / "can.log"),
            "maxBytes": 300 * 1024 * 1024,  # 修改为300MB
            "backupCount": 5,
            "encoding": "utf8"
        }
    },
    
    "loggers": {
        "": {  # root logger
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False
        },
        "app": {
            "handlers": ["console", "file_app"],
            "level": "INFO",
            "propagate": False
        },
        "can": {
            "handlers": ["file_can"],
            "level": "DEBUG",
            "propagate": False
        },
        "can.vector": {
            "handlers": ["file_can"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

def setup_logging():
    """
    配置项目日志系统
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info("日志系统已初始化")


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger("app")
    logger.info("日志配置测试")
    
    can_logger = logging.getLogger("can.vector")
    can_logger.debug("CAN日志测试") 