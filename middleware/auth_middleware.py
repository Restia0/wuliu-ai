from fastapi import Request, HTTPException, status

from dao.user_dao import user_dao
from utils.jwt_utils import verify_access_token


async def auth_middleware(request: Request, call_next):
    """
    JWT权限中间件：
    1. 排除无需校验的接口（登录/注册/健康检查）
    2. 校验令牌有效性
    3. 将用户信息存入request.state
    :param request:
    :param call_next:
    :return:
    """
    # 无需校验的路径
    exclude_paths = ["/api/v1/user/register", "/api/v1/user/login", "/health", "/docs", "/openapi.json"]
    if request.url.path in exclude_paths:
        return await call_next(request)

    # 提取令牌（兼容Bearer + token的格式）
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请求头中未找到Authorization字段"
        )

    # 校验令牌格式（Bearer + 空格 + token）
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization格式错误，正确格式：Bearer <token>"
        )
    token = parts[1]

    # 校验令牌
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌已过期或无效")

    # 验证用户是否存在
    user_id = int(payload["sub"])
    user = user_dao.get_user_by_id(user_id)
    if not user or user.get("is_delete") == 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已删除")

    # 将用户信息存入request.state（供接口层使用）
    request.state.user_id = user_id
    request.state.username = payload["username"]
    request.state.role = payload["role"]

    # 继续处理请求
    response = await call_next(request)
    return response

