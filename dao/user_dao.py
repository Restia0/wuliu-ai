from config.database import BaseDAO, db_session
from models.db_model.core_user import CoreUser
from utils.password_utils import hash_password
from sqlalchemy.exc import IntegrityError


class UserDAO(BaseDAO):
    def __init__(self):
        super.__init__(CoreUser)

    def create_user(self, user_data: dict) -> CoreUser:
        """
        创建用户（加密密码）
        :param user_data:
        :return:
        """
        user_data["password"] = hash_password(user_data["password"])
        with db_session() as db:
            try:
                user = self.create(db, user_data)
                return user
            except IntegrityError:
                # 用户名/手机号重复
                raise ValueError("用户名或手机号已存在")

    def get_user_by_username(self, username: str) -> CoreUser | None:
        """
        通过用户名查询用户
        :param username:
        :return:
        """
        with db_session() as db:
            user = self.get_by_conditions(db, {"username": username, "is_deleted": 0})
            return user

    def get_user_by_id(self, user_id: int) -> CoreUser | None:
        """
        通过ID查询用户
        :param user_id:
        :return:
        """
        with db_session() as db:
            user = self.get_by_id(db, user_id)
            return user


# 创建DAO实例（供service层调用）
user_dao = UserDAO()
