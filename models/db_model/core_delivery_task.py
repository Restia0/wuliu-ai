from sqlalchemy import Column, BIGINT, DATETIME, VARCHAR, ForeignKey
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class CoreDeliveryTask(Base):
    __tablename__ = "core_delivery_task"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="任务ID")
    order_id = Column(BIGINT, ForeignKey("core_order.id", ondelete="CASCADE"), nullable=False, comment="关联订单ID")
    driver_id = Column(BIGINT, ForeignKey("core_user.id", ondelete="CASCADE"), nullable=False, comment="关联司机ID")
    task_status = Column(ENUM("pending", "delivering", "completed", "cancelled"), default="pending", comment="任务状态")
    assign_time = Column(DATETIME, default=func.now(), comment="分配时间")
    assign_user_id = Column(BIGINT, nullable=True, comment="分配人ID（管理员）")
    complete_time = Column(DATETIME, nullable=True, comment="完成时间")
    delivery_notes = Column(VARCHAR(200), nullable=True, comment="配送备注")

    # 关联关系
    order = relationship("CoreOrder", back_populates="delivery_task")
    driver = relationship("CoreUser", back_populates="delivery_tasks")
    track_records = relationship("CoreDeliveryTrack", back_populates="task")

    def __repr__(self):
        return f"<CoreDeliveryTask(order_id={self.order_id}, driver_id={self.driver_id}, status={self.task_status})>"

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "driver_id": self.driver_id,
            "task_status": self.task_status,
            "assign_time": self.assign_time.strftime("%Y-%m-%d %H:%M:%S") if self.assign_time else None,
            "complete_time": self.complete_time.strftime("%Y-%m-%d %H:%M:%S") if self.complete_time else None,
            "delivery_notes": self.delivery_notes
        }