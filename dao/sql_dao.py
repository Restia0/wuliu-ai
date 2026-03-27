from config.database import BaseDAO, db_session
from models.db_model.ai_model.ai_sql_record import AISqlRecord


class SqlDAO(BaseDAO):
    def __init__(self):
        super().__init__(AISqlRecord)

    def save_record(self, user_id: int, question: str, sql: str = None, result: list | dict = None, answer: str = None) -> int:
        with db_session() as db:
            record = self.create(db, {
                "user_id": user_id,
                "natural_language": question,
                "generated_sql": sql,
                "query_result": result,
                "answer": answer
            })
            return record.id


sql_dao = SqlDAO()
