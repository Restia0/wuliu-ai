"""通用工具类：日志、时间、数据校验等"""
import logging
import os
from config.settings import settings

# 创建日志目录
os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE_PATH, encoding="utf-8"),  # 文件日志
        logging.StreamHandler()  # 控制台日志
    ]
)

# 创建日志实例
logger = logging.getLogger("智慧物流管理系统")