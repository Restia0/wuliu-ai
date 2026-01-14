from sqlalchemy import Column, BIGINT, VARCHAR, INT, DATETIME, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class CoreOutbound(Base):
    __tablename__ = "core_outbound"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="出库ID")
    warehouse_id = Column(BIGINT, ForeignKey("core_warehouse.id", ondelete="CASCADE"), nullable=False, comment="仓库ID")
    order_id = Column(BIGINT, ForeignKey("core_order.id", ondelete="CASCADE"), nullable=False, comment="关联订单ID")
    goods_type = Column(VARCHAR(30), nullable=True, comment="货物类型")
    goods_quantity = Column(INT, nullable=False, comment="出库数量")
    outbound_time = Column(DATETIME, default=func.now(), comment="出库时间")
    operator_id = Column(BIGINT, nullable=True, comment="操作人ID")

    # 关联关系
    warehouse = relationship("CoreWarehouse", back_populates="outbound_records")
    order = relationship("CoreOrder", back_populates="outbound_record")

    def __repr__(self):
        return f"<CoreOutbound(warehouse_id={self.warehouse_id}, order_id={self.order_id}, quantity={self.goods_quantity})>"

    def to_dict(self):
        return {
            "id": self.id,
            "warehouse_id": self.warehouse_id,
            "order_id": self.order_id,
            "goods_type": self.goods_type,
            "goods_quantity": self.goods_quantity,
            "outbound_time": self.outbound_time.strftime("%Y-%m-%d %H:%M:%S") if self.outbound_time else None,
            "operator_id": self.operator_id
        }