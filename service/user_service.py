from dao.user_dao import user_dao
from models.schema.user_schema import UserCreateRequest, UserUpdateRequest, PasswordResetRequest
from utils.jwt_utils import create_access_token
from utils.password_utils import verify_password


class UserService:
    def register(self, user_request: UserCreateRequest) -> dict:
        """
        用户注册
        :param user_request:
        :return:
        """
        # 转换为字典（过滤Pydantic额外字段）
        user_data = user_request.dict()
        user = user_dao.create_user(user_data)
        return user

    def login(self, username: str, password: str) -> tuple[str, dict] | None:
        """
        用户登录：验证成功返回令牌和用户信息
        :param username:
        :param password:
        :return:
        """
        user = user_dao.get_user_by_username(username)
        user_password = user.pop("password")
        if not user:
            return None
        # 验证密码
        if not verify_password(password, user_password):
            return None

        # 生成JWT令牌
        token = create_access_token(user['id'], user['username'], user['role'])
        return token, user

    def get_user_info(self, user_id: int) -> dict | None:
        """
        查询用户信息
        :param user_id:
        :return:
        """
        return user_dao.get_user_by_id(user_id)

    def update_user_info(self, user_id: int, user_request: UserUpdateRequest) -> dict | None:
        """
        修改用户信息
        :param user_id:
        :param user_request:
        :return:
        """
        update_data = user_request.dict(exclude_unset=True)  # 只更新传入的字段
        user = user_dao.update_user_info(user_id, update_data)
        return user

    def reset_password(self, user_id: int, reset_request: PasswordResetRequest) -> bool:
        """
        重置密码
        :param user_id:
        :param reset_request:
        :return:
        """
        # 先验证原密码
        user = user_dao.get_user_by_id(user_id)
        if not user or not verify_password(reset_request.old_password, user["password"]):
            return False
        return user_dao.reset_password(user_id, reset_request.new_password)


user_service = UserService()
