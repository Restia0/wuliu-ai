from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, DATETIME, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class SysOperationLog(Base):
    __tablename__ = "sys_operation_log"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="日志ID")
    user_id = Column(BIGINT, ForeignKey("core_user.id", ondelete="SET NULL"), nullable=True, comment="操作人ID")
    operation_module = Column(VARCHAR(50), nullable=True, comment="操作模块（如：订单管理/AI OCR）")
    operation_type = Column(VARCHAR(20), nullable=True, comment="操作类型（新增/修改/删除/查询）")
    operation_content = Column(TEXT, nullable=True, comment="操作内容")
    ip_address = Column(VARCHAR(50), nullable=True, comment="操作IP")
    operation_time = Column(DATETIME, default=func.now(), comment="操作时间")

    # 关联关系
    user = relationship("CoreUser", backref="operation_logs")

    def __repr__(self):
        return f"<SysOperationLog(user_id={self.user_id}, module={self.operation_module}, type={self.operation_type})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "operation_module": self.operation_module,
            "operation_type": self.operation_type,
            "operation_content": self.operation_content,
            "ip_address": self.ip_address,
            "operation_time": self.operation_time.strftime("%Y-%m-%d %H:%M:%S") if self.operation_time else None
        }