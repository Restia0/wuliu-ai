"""
全局配置文件：统一管理项目配置，避免硬编码
"""
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Settings:
    # 基础配置
    PROJECT_NAME = os.getenv("PROJECT_NAME", "智慧物流管理系统")
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # MySQL配置
    MYSQL_URL = os.getenv("MYSQL_URL")
    MYSQL_POOL_SIZE = int(os.getenv("MYSQL_POOL_SIZE", 10))
    MYSQL_MAX_OVERFLOW = int(os.getenv("MYSQL_MAX_OVERFLOW", 20))

    # # Milvus配置
    # MILVUS_URI = os.getenv("MILVUS_URI", "./milvus_demo.db")
    # MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "logistics_faq")
    # MILVUS_VECTOR_DIM = int(os.getenv("MILVUS_VECTOR_DIM", 768))
    #
    # # 大模型配置
    # LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
    # LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")

    # JWT配置
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 86400))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    #
    # # 静态资源配置
    # STATIC_IMAGE_PATH = os.getenv("STATIC_IMAGE_PATH", "./static/images")
    # STATIC_HTML_PATH = os.getenv("STATIC_HTML_PATH", "./static/html")

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "./logs/app.log")


# 创建配置实例
settings = Settings()