from sqlalchemy import Column, BIGINT, VARCHAR, DATETIME, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class CoreDeliveryTrack(Base):
    __tablename__ = "core_delivery_track"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="轨迹ID")
    task_id = Column(BIGINT, ForeignKey("core_delivery_task.id", ondelete="CASCADE"), nullable=False,
                     comment="关联任务ID")
    track_node = Column(VARCHAR(50), nullable=True, comment="轨迹节点（如：已取货/到达配送点）")
    track_time = Column(DATETIME, default=func.now(), comment="节点时间")
    track_address = Column(VARCHAR(200), nullable=True, comment="节点地址")
    driver_id = Column(BIGINT, nullable=True, comment="操作司机ID")

    # 关联关系
    task = relationship("CoreDeliveryTask", back_populates="track_records")

    def __repr__(self):
        return f"<CoreDeliveryTrack(task_id={self.task_id}, node={self.track_node}, time={self.track_time})>"

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "track_node": self.track_node,
            "track_time": self.track_time.strftime("%Y-%m-%d %H:%M:%S") if self.track_time else None,
            "track_address": self.track_address,
            "driver_id": self.driver_id
        }