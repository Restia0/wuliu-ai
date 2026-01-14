from datetime import datetime, timedelta
import jwt
from config.settings import settings


def create_access_token(user_id: int, username: str, role: str) -> str:
    """
    生成JWT令牌
    :param user_id:
    :param username:
    :param role:
    :return:
    """
    # 载荷：存储用户核心信息（避免敏感数据）
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS)
    }

    # 加密生成令牌
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def verify_access_token(token: str) -> dict:
    """
    验证JWT令牌
    :param token:
    :return:
    """
    try:
        # 解密令牌
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("令牌已过期")
    except jwt.InvalidTokenError:
        raise Exception("令牌无效")
