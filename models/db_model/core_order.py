from sqlalchemy import Column, BIGINT, VARCHAR, INT, DATETIME, ForeignKey
from sqlalchemy.dialects.mysql import ENUM, TINYINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class CoreOrder(Base):
    __tablename__ = "core_order"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="订单ID")
    order_no = Column(VARCHAR(30), unique=True, nullable=False, comment="订单号（时间戳+随机数）")
    # 发件人信息
    sender_name = Column(VARCHAR(50), nullable=True, comment="发件人姓名")
    sender_phone = Column(VARCHAR(20), nullable=True, comment="发件人手机号")
    sender_province = Column(VARCHAR(20), nullable=True, comment="发件省")
    sender_city = Column(VARCHAR(20), nullable=True, comment="发件市")
    sender_district = Column(VARCHAR(20), nullable=True, comment="发件区/县")
    sender_address = Column(VARCHAR(200), nullable=True, comment="发件详细地址")
    # 收件人信息
    receiver_name = Column(VARCHAR(50), nullable=True, comment="收件人姓名")
    receiver_phone = Column(VARCHAR(20), nullable=True, comment="收件人手机号")
    receiver_province = Column(VARCHAR(20), nullable=True, comment="收件省")
    receiver_city = Column(VARCHAR(20), nullable=True, comment="收件市")
    receiver_district = Column(VARCHAR(20), nullable=True, comment="收件区/县")
    receiver_address = Column(VARCHAR(200), nullable=True, comment="收件详细地址")
    # 货物信息
    goods_type = Column(VARCHAR(30), nullable=True, comment="货物类型（普通/易碎/大件）")
    goods_quantity = Column(INT, default=1, comment="货物数量")
    # 状态/关联信息
    order_status = Column(ENUM("pending", "delivering", "signed", "cancelled"), default="pending", comment="订单状态")
    driver_id = Column(BIGINT, ForeignKey("core_user.id", ondelete="SET NULL"), nullable=True, comment="关联司机ID")
    warehouse_id = Column(BIGINT, ForeignKey("core_warehouse.id", ondelete="SET NULL"), nullable=True,
                          comment="关联出库仓库ID")
    create_user_id = Column(BIGINT, nullable=True, comment="创建人ID")
    # 时间/删除标记
    create_time = Column(DATETIME, default=func.now(), comment="创建时间")
    update_time = Column(DATETIME, default=func.now(), onupdate=func.now(), comment="更新时间")
    is_delete = Column(TINYINT, default=0, comment="是否删除")

    # 关联关系
    driver = relationship("CoreUser", foreign_keys=[driver_id], backref="assigned_orders")
    warehouse = relationship("CoreWarehouse", back_populates="orders")
    delivery_task = relationship("CoreDeliveryTask", back_populates="order", uselist=False)
    ocr_record = relationship("AIOcrRecord", back_populates="order", uselist=False)
    inbound_record = relationship("CoreInbound", back_populates="order", uselist=False)
    outbound_record = relationship("CoreOutbound", back_populates="order", uselist=False)

    def __repr__(self):
        return f"<CoreOrder(order_no={self.order_no}, status={self.order_status}, driver_id={self.driver_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "order_no": self.order_no,
            "sender_info": {
                "name": self.sender_name,
                "phone": self.sender_phone,
                "address": f"{self.sender_province}{self.sender_city}{self.sender_district}{self.sender_address}"
            },
            "receiver_info": {
                "name": self.receiver_name,
                "phone": self.receiver_phone,
                "address": f"{self.receiver_province}{self.receiver_city}{self.receiver_district}{self.receiver_address}"
            },
            "goods_info": {
                "type": self.goods_type,
                "quantity": self.goods_quantity
            },
            "status": self.order_status,
            "driver_id": self.driver_id,
            "warehouse_id": self.warehouse_id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None
        }