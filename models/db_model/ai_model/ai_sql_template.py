from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, DATETIME
from sqlalchemy.sql import func
from config.database import Base


class AISqlTemplate(Base):
    __tablename__ = "ai_sql_template"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="模板ID")
    template_name = Column(VARCHAR(50), nullable=False, comment="模板名称")
    intent_keywords = Column(VARCHAR(100), nullable=False, comment="意图关键词")
    sql_template = Column(TEXT, nullable=False, comment="SQL模板")
    create_time = Column(DATETIME, default=func.now(), comment="创建时间")
    update_time = Column(DATETIME, default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<AISqlTemplate(id={self.id}, name={self.template_name}, keywords={self.intent_keywords})>"

    def to_dict(self):
        return {
            "id": self.id,
            "template_name": self.template_name,
            "intent_keywords": self.intent_keywords,
            "sql_template": self.sql_template,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None
        }