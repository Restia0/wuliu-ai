from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, JSON, DATETIME, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class AIOcrRecord(Base):
    __tablename__ = "ai_ocr_record"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="记录ID")
    order_id = Column(BIGINT, ForeignKey("core_order.id", ondelete="CASCADE"), nullable=True, comment="关联订单ID")
    ocr_image_url = Column(VARCHAR(200), nullable=True, comment="单据图片路径")
    ocr_text = Column(TEXT, nullable=True, comment="OCR识别文本")
    extract_result = Column(JSON, nullable=True, comment="大模型提取结果（JSON）")
    create_user_id = Column(BIGINT, nullable=True, comment="操作人ID")
    create_time = Column(DATETIME, default=func.now(), comment="识别时间")

    # 关联关系
    order = relationship("CoreOrder", back_populates="ocr_record")

    def __repr__(self):
        return f"<AIOcrRecord(order_id={self.order_id}, image={self.ocr_image_url[:20]}...)>"

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "ocr_image_url": self.ocr_image_url,
            "ocr_text": self.ocr_text[:100] + "..." if self.ocr_text and len(self.ocr_text) > 100 else self.ocr_text,
            "extract_result": self.extract_result,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None
        }