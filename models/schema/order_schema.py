from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, List
import re
from datetime import datetime

# 订单状态枚举
OrderStatus = Literal["pending", "delivering", "signed", "cancelled"]


# 基础订单模型（公共字段）
class OrderBase(BaseModel):
    # 发件人信息
    sender_name: Optional[str] = Field(None, max_length=50, description="发件人姓名")
    sender_phone: Optional[str] = Field(None, description="发件人手机号")
    sender_province: Optional[str] = Field(None, max_length=20, description="发件省")
    sender_city: Optional[str] = Field(None, max_length=20, description="发件市")
    sender_district: Optional[str] = Field(None, max_length=20, description="发件区/县")
    sender_address: Optional[str] = Field(None, max_length=200, description="发件详细地址")
    # 收件人信息
    receiver_name: Optional[str] = Field(None, max_length=50, description="收件人姓名")
    receiver_phone: Optional[str] = Field(None, description="收件人手机号")
    receiver_province: Optional[str] = Field(None, max_length=20, description="收件省")
    receiver_city: Optional[str] = Field(None, max_length=20, description="收件市")
    receiver_district: Optional[str] = Field(None, max_length=20, description="收件区/县")
    receiver_address: Optional[str] = Field(None, max_length=200, description="收件详细地址")
    # 货物信息
    goods_type: Optional[str] = Field(None, max_length=30, description="货物类型（普通/易碎/大件）")
    goods_quantity: int = Field(default=1, ge=1, description="货物数量（至少1件）")
    # 关联信息
    warehouse_id: Optional[int] = Field(None, description="关联仓库ID")

    # 手机号格式校验
    @validator("sender_phone", "receiver_phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式错误")
        return v


# 订单创建请求模型
class OrderCreateRequest(BaseModel):
    # 发件人信息
    sender_name: str = Field(..., max_length=50, description="发件人姓名")  # 改为必传
    sender_phone: str = Field(..., description="发件人手机号")  # 改为必传
    sender_province: str = Field(..., max_length=20, description="发件省")
    sender_city: str = Field(..., max_length=20, description="发件市")
    sender_district: str = Field(..., max_length=20, description="发件区/县")
    sender_address: str = Field(..., max_length=200, description="发件详细地址")
    # 收件人信息
    receiver_name: str = Field(..., max_length=50, description="收件人姓名")
    receiver_phone: str = Field(..., description="收件人手机号")
    receiver_province: str = Field(..., max_length=20, description="收件省")
    receiver_city: str = Field(..., max_length=20, description="收件市")
    receiver_district: str = Field(..., max_length=20, description="收件区/县")
    receiver_address: str = Field(..., max_length=200, description="收件详细地址")
    # 货物信息
    goods_type: Optional[str] = Field(None, max_length=30, description="货物类型（普通/易碎/大件）")
    goods_quantity: int = Field(default=1, ge=1, description="货物数量（至少1件）")

    # 手机号校验器保留
    @validator("sender_phone", "receiver_phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式错误")
        return v


# 订单状态修改请求模型
class OrderStatusUpdateRequest(BaseModel):
    order_status: OrderStatus = Field(description="订单状态")
    driver_id: Optional[int] = Field(None, description="关联司机ID（仅状态为delivering时必填）")

    @validator("driver_id")
    def validate_driver_id(cls, v, values):
        if values.get("order_status") == "delivering" and not v:
            raise ValueError("订单状态改为配送中时，必须指定司机ID")
        return v


# 订单查询筛选条件
class OrderQueryRequest(BaseModel):
    order_no: Optional[str] = Field(None, description="订单号")
    order_status: Optional[OrderStatus] = Field(None, description="订单状态")
    warehouse_id: Optional[int] = Field(None, description="仓库ID")
    driver_id: Optional[int] = Field(None, description="司机ID")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=50, description="每页条数")


# 订单详情响应模型
class OrderDetailResponse(BaseModel):
    id: int
    order_no: str
    # 发件人信息
    sender_name: Optional[str]
    sender_phone: Optional[str]
    sender_address: Optional[str]  # 拼接后的完整地址
    # 收件人信息
    receiver_name: Optional[str]
    receiver_phone: Optional[str]
    receiver_address: Optional[str]  # 拼接后的完整地址
    # 货物信息
    goods_type: Optional[str]
    goods_quantity: int
    # 状态/关联信息
    order_status: str
    driver_id: Optional[int]
    warehouse_id: Optional[int]
    create_user_id: Optional[int]
    # 时间信息
    create_time: str
    update_time: str

    # 支持字典/ORM对象序列化
    class Config:
        from_attributes = True


# 订单列表响应模型
class OrderListResponse(BaseModel):
    total: int  # 总条数
    page: int
    page_size: int
    data: List[OrderDetailResponse]
