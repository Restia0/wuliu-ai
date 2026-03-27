from dao.sql_dao import sql_dao
from models.schema.sql_schema import TextToSqlRequest
from utils.sql_utils import agent_text_to_sql


class SqlService:
    def query(self, req: TextToSqlRequest, user_id: int) -> dict:
        question = req.question
        result = agent_text_to_sql(question)

        record_id = sql_dao.save_record(
            user_id,
            question,
            result.get("generated_sql"),
            result.get("query_result"),
            result.get("answer")
        )

        return {
            "question": question,
            "generated_sql": result.get("generated_sql"),
            "query_result": result.get("query_result"),
            "answer": result.get("answer"),
            "record_id": record_id
        }


sql_service = SqlService()
