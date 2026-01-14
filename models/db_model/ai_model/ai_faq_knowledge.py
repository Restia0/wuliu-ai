from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, DATETIME
from sqlalchemy.sql import func
from config.database import Base


class AIFaqKnowledge(Base):
    __tablename__ = "ai_faq_knowledge"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="知识库ID")
    question = Column(VARCHAR(200), nullable=False, comment="问题")
    answer = Column(TEXT, nullable=False, comment="标准答案")
    keywords = Column(VARCHAR(100), nullable=True, comment="关键词（分词后）")
    embedding_vector = Column(TEXT, nullable=True, comment="向量值（768维，JSON字符串）")
    create_time = Column(DATETIME, default=func.now(), comment="创建时间")
    update_time = Column(DATETIME, default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<AIFaqKnowledge(id={self.id}, question={self.question[:20]}...)>"

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "keywords": self.keywords,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None
        }