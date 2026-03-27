from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class TextToSqlRequest(BaseModel):
    question: str = Field(..., description="用户输入的问题")


class TextToSqlResponse(BaseModel):
    question: str
    generated_sql: Optional[str]
    query_result: Optional[str]
    answer: Optional[str]
    record_id: int
