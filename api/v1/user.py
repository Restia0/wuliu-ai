from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer

from models.schema.user_schema import UserCreateRequest, UserInfoResponse, UserLoginRequest, UserLoginResponse, \
    UserUpdateRequest, PasswordResetRequest
from service.user_service import user_service
from utils.common_utils import logger

# 新增：定义OAuth2依赖（适配Swagger Docs）
bearer_scheme = HTTPBearer(auto_error=False)

# 创建路由实例
router = APIRouter()


@router.post("/register", summary="用户注册", response_model=UserInfoResponse)
def user_register(request: UserCreateRequest):
    """
    用户注册接口
    :param request:
    :return:
    """
    try:
        user = user_service.register(request)
        logger.info(f"用户注册成功：{user['username']}（角色：{user['role']}）")
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"用户注册失败：{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="注册失败")


@router.post("/login", summary="用户登录", response_model=UserLoginResponse)
def user_login(request: UserLoginRequest):
    """
    用户登录接口
    :param request:
    :return:
    """
    result = user_service.login(request.username, request.password)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token, user = result
    logger.info(f"用户登录成功：{user['username']}")
    return {
        "access_token": token,
        "user_info": user
    }


@router.get("/info", summary="查询当前用户信息", response_model=UserInfoResponse, dependencies=[Depends(bearer_scheme)])
def get_user_info(request: Request):
    """
    查询当前登录用户信息（从request.state获取用户ID）
    :param request:
    :return:
    """
    user = user_service.get_user_info(request.state.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在或已删除")
    del user["password"]
    return user


@router.put("/info", summary="修改当前用户信息", response_model=UserInfoResponse, dependencies=[Depends(bearer_scheme)])
def update_user_info(request: Request, update_data: UserUpdateRequest):
    """
    修改当前登录用户信息
    :param request:
    :param update_data:
    :return:
    """
    user = user_service.update_user_info(request.state.user_id, update_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在或已删除")
    logger.info(f"用户信息修改成功：{user['username']}")
    del user["password"]
    return user


@router.put("/reset-password", summary="重置密码", dependencies=[Depends(bearer_scheme)])
def reset_password(request: Request, reset_data: PasswordResetRequest):
    """
    重置当前登录用户密码
    :param request:
    :param reset_data:
    :return:
    """
    success = user_service.reset_password(request.state.user_id, reset_data)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    logger.info(f"用户密码重置成功：{request.state.username}")
    return {"code": 200, "message": "密码重置成功"}
