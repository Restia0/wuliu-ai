from fastapi import APIRouter, HTTPException, status

from models.schema.user_schema import UserCreateRequest, UserInfoResponse
from service.user_service import user_service
from utils.common_utils import logger

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
