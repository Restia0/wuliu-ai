from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse

from config.database import init_db
from config.settings import settings
from middleware.auth_middleware import auth_middleware

from api.v1.user import router as user_router
from api.v1.order import router as order_router
from api.v1.warehouse import router as warehouse_router
from api.v1.delivery import router as delivery_router
from api.v1.ocr import router as ocr_router
from api.v1.sql import router as sql_router
from middleware.log_middleware import log_middleware


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

# 权限拦截中间件（验证JWT令牌）
# 注意：后注册的先执行
app.middleware("http")(log_middleware)
app.middleware("http")(auth_middleware)

# 注册路由
# 核心业务模块路由
app.include_router(user_router, prefix="/api/v1/user", tags=["用户与权限管理"])
app.include_router(order_router, prefix="/api/v1/order", tags=["订单管理"])
app.include_router(warehouse_router, prefix="/api/v1/warehouse", tags=["仓库管理"])
app.include_router(delivery_router, prefix="/api/v1/delivery", tags=["配送管理"])
app.include_router(ocr_router, prefix="/api/v1/ocr", tags=["ocr功能"])
app.include_router(sql_router, prefix="/api/v1/sql", tags=["智能查询"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT)
