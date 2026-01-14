from sqlalchemy import Column, BIGINT, TEXT, DATETIME, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class AIChatRecord(Base):
    __tablename__ = "ai_chat_record"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="对话ID")
    user_id = Column(BIGINT, ForeignKey("core_user.id", ondelete="CASCADE"), nullable=False, comment="提问用户ID")
    user_question = Column(TEXT, nullable=False, comment="用户问题")
    rag_context = Column(TEXT, nullable=True, comment="RAG检索上下文")
    ai_answer = Column(TEXT, nullable=True, comment="AI回答")
    chat_time = Column(DATETIME, default=func.now(), comment="对话时间")

    # 关联关系
    user = relationship("CoreUser", backref="chat_records")

    def __repr__(self):
        return f"<AIChatRecord(user_id={self.user_id}, question={self.user_question[:20]}...)>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_question": self.user_question,
            "ai_answer": self.ai_answer,
            "chat_time": self.chat_time.strftime("%Y-%m-%d %H:%M:%S") if self.chat_time else None
        }