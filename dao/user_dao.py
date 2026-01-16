from config.database import BaseDAO, db_session
from models.db_model.core_user import CoreUser
from utils.password_utils import hash_password
from sqlalchemy.exc import IntegrityError


class UserDAO(BaseDAO):
    def __init__(self):
        super().__init__(CoreUser)

    def create_user(self, user_data: dict) -> dict:
        """
        创建用户（加密密码）
        :param user_data:
        :return:
        """
        user_data["password"] = hash_password(user_data["password"])
        with db_session() as db:
            try:
                user = self.create(db, user_data)
                user_dict = user.to_dict()
                return user_dict
            except IntegrityError:
                # 用户名/手机号重复
                raise ValueError("用户名或手机号已存在")

    def get_user_by_username(self, username: str) -> dict | None:
        """
        通过用户名查询用户
        :param username:
        :return:
        """
        with db_session() as db:
            user = self.get_by_conditions(db, {"username": username, "is_delete": 0})
            user_dict = user.to_dict()
            return user_dict

    def get_user_by_id(self, user_id: int) -> dict | None:
        """
        通过ID查询用户
        :param user_id:
        :return:
        """
        with db_session() as db:
            user = self.get_by_id(db, user_id)
            user_dict = user.to_dict()
            return user_dict

    def update_user_info(self, user_id: int, update_data: dict) -> dict | None:
        """
        修改用户信息（不含密码）
        :param user_id:
        :param update_data:
        :return:
        """
        with db_session() as db:
            user = self.get_by_id(db, user_id)
            if not user:
                return None
            # 只更新允许修改的字段
            allowed_fields = ["phone", "real_name"]
            update_data = {k: v for k, v in update_data.items() if k in allowed_fields}
            user = self.update(db, user, update_data)
            user_dict = user.to_dict()
            return user_dict

    def reset_password(self, user_id: int, new_password: str) -> bool:
        """
        重置密码（加密存储）
        :param user_id:
        :param new_password:
        :return:
        """
        with db_session() as db:
            user = self.get_by_id(db, user_id)
            if not user:
                return False
            user = self.update(db, user, {"password": hash_password(new_password)})
            return True


# 创建DAO实例（供service层调用）
user_dao = UserDAO()
