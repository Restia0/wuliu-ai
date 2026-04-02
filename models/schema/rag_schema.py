from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., description="用户问题")


class ChatResponse(BaseModel):
    question: str = Field(..., description="用户问题")
    answer: str = Field(..., description="AI回答")
    record_id: int = Field(..., description="记录ID")
