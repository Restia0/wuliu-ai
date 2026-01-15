from dao.user_dao import user_dao
from models.schema.user_schema import UserCreateRequest


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


user_service = UserService()
