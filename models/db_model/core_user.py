from sqlalchemy import Column, BIGINT, VARCHAR, DATETIME
from sqlalchemy.dialects.mysql import ENUM, TINYINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class CoreUser(Base):
    __tablename__ = "core_user"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(VARCHAR(50), unique=True, nullable=False, comment="用户名")
    password = Column(VARCHAR(100), nullable=False, comment="加密密码")
    role = Column(ENUM("admin", "driver", "customer"), nullable=False, comment="角色")
    phone = Column(VARCHAR(20), unique=True, nullable=True, comment="手机号")
    real_name = Column(VARCHAR(50), nullable=True, comment="真实姓名")
    create_time = Column(DATETIME, default=func.now(), comment="创建时间")
    update_time = Column(DATETIME, default=func.now(), onupdate=func.now(), comment="更新时间")
    is_delete = Column(TINYINT, default=0, comment="是否删除（0-否，1-是）")

    # 关联关系
    driver_ext = relationship("CoreDriverExt", back_populates="user", uselist=False)
    delivery_tasks = relationship("CoreDeliveryTask", back_populates="driver")
    created_orders = relationship("CoreOrder",
                                  foreign_keys="[CoreOrder.create_user_id]",
                                  primaryjoin="CoreUser.id == CoreOrder.create_user_id",
                                  back_populates="creator",
                                  lazy="dynamic",
                                  )

    def __repr__(self):
        return f"<CoreUser(id={self.id}, username={self.username}, role={self.role})>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "phone": self.phone,
            "real_name": self.real_name,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None
        }
