from sqlalchemy import Column, BIGINT, TEXT, JSON, DATETIME, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class AISqlRecord(Base):
    __tablename__ = "ai_sql_record"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BIGINT, ForeignKey("core_user.id", ondelete="CASCADE"), nullable=False,
                     comment="操作人ID（仅管理员）")
    natural_language = Column(TEXT, nullable=False, comment="自然语言提问")
    extract_params = Column(JSON, nullable=True, comment="提取的参数")
    generated_sql = Column(TEXT, nullable=True, comment="生成的SQL")
    query_result = Column(JSON, nullable=True, comment="查询结果")
    call_time = Column(DATETIME, default=func.now(), comment="调用时间")

    # 关联关系
    user = relationship("CoreUser", backref="sql_records")

    def __repr__(self):
        return f"<AISqlRecord(user_id={self.user_id}, query={self.natural_language[:20]}...)>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "natural_language": self.natural_language,
            "generated_sql": self.generated_sql,
            "query_result": self.query_result,
            "call_time": self.call_time.strftime("%Y-%m-%d %H:%M:%S") if self.call_time else None
        }