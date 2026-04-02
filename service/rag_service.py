from dao.rag_dao import chat_record_dao
from models.schema.rag_schema import ChatRequest
from utils.rag_utils import rag_agent_run, rag_retrieve, upload_pdf_to_vector_db


class RagService:
    def chat(self, raq: ChatRequest, user_id: int):
        question = raq.question
        answer = rag_agent_run(question)

        # 记录对话
        record_id = chat_record_dao.save_record(
            user_id=user_id,
            question=question,
            context=rag_retrieve(question),
            answer=answer
        )

        return {
            "question": question,
            "answer": answer,
            "record_id": record_id
        }

    def upload_pdf(self, pdf_path: str):
        count = upload_pdf_to_vector_db(pdf_path)
        return {
            "status": "success",
            "chunk_count": count
        }


rag_service = RagService()
