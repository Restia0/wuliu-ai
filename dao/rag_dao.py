from config.database import BaseDAO, db_session
from models.db_model.ai_model.ai_chat_record import AIChatRecord


class ChatRecordDAO(BaseDAO):
    def __init__(self):
        super().__init__(AIChatRecord)

    def save_record(self, user_id: int, question: str, context: str, answer: str = None):
        with db_session() as db:
            record = self.create(db, {
                "user_id": user_id,
                "user_question": question,
                "rag_context": context,
                "ai_answer": answer
            })
            return record.id


chat_record_dao = ChatRecordDAO()
