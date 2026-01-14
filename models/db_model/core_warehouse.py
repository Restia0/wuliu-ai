from sqlalchemy import Column, BIGINT, VARCHAR, INT, DATETIME, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class CoreWarehouse(Base):
    __tablename__ = "core_warehouse"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="仓库ID")
    warehouse_name = Column(VARCHAR(50), nullable=False, comment="仓库名称")
    province = Column(VARCHAR(20), nullable=True, comment="仓库省")
    city = Column(VARCHAR(20), nullable=True, comment="仓库市")
    district = Column(VARCHAR(20), nullable=True, comment="仓库区/县")
    address = Column(VARCHAR(200), nullable=True, comment="仓库详细地址")
    capacity_limit = Column(INT, nullable=False, comment="库存容量上限（件）")
    current_stock = Column(INT, default=0, comment="当前库存")
    manager_id = Column(BIGINT, ForeignKey("core_user.id", ondelete="SET NULL"), nullable=True, comment="仓库管理员ID")
    create_time = Column(DATETIME, default=func.now(), comment="创建时间")
    update_time = Column(DATETIME, default=func.now(), onupdate=func.now(), comment="更新时间")
    is_delete = Column(TINYINT, default=0, comment="是否删除")

    # 关联关系
    manager = relationship("CoreUser", backref="managed_warehouses")
    orders = relationship("CoreOrder", back_populates="warehouse")
    inbound_records = relationship("CoreInbound", back_populates="warehouse")
    outbound_records = relationship("CoreOutbound", back_populates="warehouse")

    def __repr__(self):
        return f"<CoreWarehouse(id={self.id}, name={self.warehouse_name}, stock={self.current_stock}/{self.capacity_limit})>"

    def to_dict(self):
        return {
            "id": self.id,
            "warehouse_name": self.warehouse_name,
            "address": f"{self.province}{self.city}{self.district}{self.address}",
            "capacity_limit": self.capacity_limit,
            "current_stock": self.current_stock,
            "manager_id": self.manager_id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None
        }