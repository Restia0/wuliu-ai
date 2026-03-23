"""通用工具类：日志、时间、数据校验等"""
import logging
import os
from logging.handlers import RotatingFileHandler
from config.settings import settings

# 创建日志目录
os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)

# 1. 创建日志格式化器
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 2. 文件日志（按大小轮转，避免单个文件过大）
file_handler = RotatingFileHandler(
    settings.LOG_FILE_PATH,
    maxBytes=1024 * 1024 * 50,  # 50MB
    backupCount=10,
    encoding="utf-8",
)
file_handler.setFormatter(formatter)

# 3. ERROR级别日志单独文件
error_file_handler = RotatingFileHandler(
    settings.LOG_FILE_PATH.replace(".log", "_error.log"),
    maxBytes=1024 * 1024 * 50,
    backupCount=10,
    encoding="utf-8",
)
error_file_handler.setFormatter(formatter)
error_file_handler.setLevel(logging.ERROR)

# 4. 控制台日志
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# 5.配置根日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    handlers=[file_handler, error_file_handler, console_handler]
)

# 创建日志实例
logger = logging.getLogger("智慧物流管理系统")