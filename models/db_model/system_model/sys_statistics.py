from sqlalchemy import Column, BIGINT, VARCHAR, JSON, DATETIME
from sqlalchemy.sql import func
from config.database import Base


class SysStatistics(Base):
    __tablename__ = "sys_statistics"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="报表ID")
    stat_type = Column(VARCHAR(50), nullable=False, comment="统计类型（订单统计/库存统计/AI调用统计）")
    stat_time = Column(VARCHAR(20), nullable=False, comment="统计时间（如：2026-01）")
    stat_data = Column(JSON, nullable=False, comment="统计数据（JSON）")
    create_time = Column(DATETIME, default=func.now(), comment="生成时间")
    update_time = Column(DATETIME, default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<SysStatistics(type={self.stat_type}, time={self.stat_time})>"

    def to_dict(self):
        return {
            "id": self.id,
            "stat_type": self.stat_type,
            "stat_time": self.stat_time,
            "stat_data": self.stat_data,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None
        }