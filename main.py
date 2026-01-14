from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse

from config.database import init_db
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== 项目启动中，初始化资源 ===")
    init_db()  # 初始化MySQL连接（创建会话池）
    # init_milvus()  # 初始化Milvus向量库（创建集合/加载知识库）
    print("=== 资源初始化完成，项目启动成功 ===")

    yield

    # 销毁阶段：释放资源（如关闭数据库连接、向量库连接）
    print("=== 项目关闭中，释放资源 ===")
    # 可添加：关闭数据库会话池、Milvus客户端等逻辑
    print("=== 资源释放完成，项目关闭成功 ===")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="智慧物流管理系统",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT)
