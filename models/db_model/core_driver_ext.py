from sqlalchemy import Column, BIGINT, VARCHAR, INT, FLOAT, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base


class CoreDriverExt(Base):
    __tablename__ = "core_driver_ext"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="扩展ID")
    user_id = Column(BIGINT, ForeignKey("core_user.id", ondelete="CASCADE"), nullable=False, comment="关联用户ID")
    car_no = Column(VARCHAR(20), nullable=True, comment="车牌号")
    delivery_area = Column(VARCHAR(100), nullable=True, comment="常配送区域（如：上海-浦东）")
    task_count = Column(INT, default=0, comment="待完成任务数")
    efficiency = Column(FLOAT, default=0.0, comment="配送效率（完成率）")

    # 关联关系
    user = relationship("CoreUser", back_populates="driver_ext")

    def __repr__(self):
        return f"<CoreDriverExt(user_id={self.user_id}, car_no={self.car_no}, delivery_area={self.delivery_area})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "car_no": self.car_no,
            "delivery_area": self.delivery_area,
            "task_count": self.task_count,
            "efficiency": round(self.efficiency, 2) if self.efficiency else 0.0
        }
