from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
import re
from datetime import datetime


# 仓库基础信息请求/响应模型
class WarehouseBase(BaseModel):
    warehouse_name: str = Field(..., max_length=50, description="仓库名称")
    province: Optional[str] = Field(None, max_length=20, description="仓库省")
    city: Optional[str] = Field(None, max_length=20, description="仓库市")
    district: Optional[str] = Field(None, max_length=20, description="仓库区/县")
    address: Optional[str] = Field(None, max_length=200, description="仓库详细地址")
    capacity_limit: int = Field(..., ge=1, description="库存容量上限（件）")
    manager_id: Optional[int] = Field(None, description="仓库管理员ID（关联用户ID）")


class WarehouseCreateRequest(WarehouseBase):
    """
    创建仓库请求模型
    """
    pass


class WarehouseUpdateRequest(WarehouseBase):
    """
    修改仓库请求模型
    """
    id: int = Field(..., description="仓库ID")


class WarehouseDetailResponse(BaseModel):
    """
    仓库详情响应模型
    """
    id: int
    warehouse_name: str
    province: Optional[str]
    city: Optional[str]
    district: Optional[str]
    address: Optional[str]
    capacity_limit: int
    current_stock: int
    manager_id: Optional[int]
    manager_name: Optional[str] = Field(None, description="仓库管理员姓名")
    create_time: str
    update_time: str
    stock_warning: bool = Field(False, description="是否库存预警（current_stock > 80% capacity_limit）")

    # 支持模型转DTO
    class Config:
        from_attributes = True


class WarehouseListResponse(BaseModel):
    """
    仓库列表响应模型
    """
    total: int
    page: int
    page_size: int
    data: List[WarehouseDetailResponse]


# 入库/出库模型
class InboundRequest(BaseModel):
    """
    入库请求模型
    """
    warehouse_id: int = Field(..., description="仓库ID")
    order_id: Optional[int] = Field(None, description="关联订单ID")
    goods_type: Optional[str] = Field(None, max_length=30, description="货物类型")
    goods_quantity: int = Field(..., ge=1, description="入库数量")


class OutboundRequest(BaseModel):
    """
    出库请求模型
    """
    warehouse_id: int = Field(..., description="仓库ID")
    order_id: Optional[int] = Field(None, description="关联订单ID")
    goods_type: Optional[str] = Field(None, max_length=30, description="货物类型")
    goods_quantity: int = Field(..., ge=1, description="出库数量")


class StockRecordResponse(BaseModel):
    """
    库存记录（入库/出库）响应模型
    """
    id: int
    warehouse_id: int
    warehouse_name: Optional[str]
    order_id: Optional[int]
    goods_type: Optional[str]
    goods_quantity: int
    operate_time: str
    operator_id: Optional[int]
    operator_name: Optional[str]
    operate_type: Literal["inbound", "outbound"] = Field(description="操作类型：入库/出库")


class StockQueryRequest(BaseModel):
    """
    库存查询请求模型
    """
    warehouse_id: Optional[int] = Field(None, description="仓库ID")
    warning_only: bool = Field(False, description="仅查询预警仓库（current_stock > 80% capacity_limit）")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)
