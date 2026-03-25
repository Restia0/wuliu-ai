from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import re


# OCR识别请求模型
class OcrRecognitionRequest(BaseModel):
    """# OCR识别请求模型"""
    file_path: str = Field(..., description="PDF文件本地路径/OSS URL")
    create_user_id: int = Field(..., description="操作人ID")


# OCR识别响应模型
class OcrRecognitionResponse(BaseModel):
    """OCR识别响应"""
    ocr_record_id: int
    ocr_text: str
    extract_result: Dict[str, Any]
    order_id: Optional[int] = Field(None, description="自动创建的订单ID")
    message: str = Field(..., description="处理结果")


# 大模型提取结果模型（用于校验）
class OrderExtractResult(BaseModel):
    """大模型提取的订单信息校验模型"""
    sender_name: Optional[str] = Field(None, max_length=50)
    sender_phone: Optional[str] = Field(None, max_length=20)
    sender_province: Optional[str] = Field(None, max_length=20)
    sender_city: Optional[str] = Field(None, max_length=20)
    sender_district: Optional[str] = Field(None, max_length=20)
    sender_address: Optional[str] = Field(None, max_length=200)
    receiver_name: Optional[str] = Field(None, max_length=50)
    receiver_phone: Optional[str] = Field(None, max_length=20)
    receiver_province: Optional[str] = Field(None, max_length=20)
    receiver_city: Optional[str] = Field(None, max_length=20)
    receiver_district: Optional[str] = Field(None, max_length=20)
    receiver_address: Optional[str] = Field(None, max_length=200)
    goods_type: Optional[str] = Field(None, max_length=30)
    goods_quantity: Optional[int] = Field(None, ge=1)

    @validator("sender_phone", "receiver_phone")
    def validate_phone(cls, v):
        """手机号简单校验"""
        if v and not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式错误")
        return v
