import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, validator

# 枚举类型定义
TaskStatus = Literal["pending", "delivering", "completed", "cancelled"]
TrackStatus = Literal["已取货", "运输中", "已送达"]


# 司机扩展信息模型
class DriverExtBase(BaseModel):
    user_id: int = Field(..., description="关联用户ID（司机账号）")
    car_no: Optional[str] = Field(None, max_length=20, description="车牌号")
    delivery_area: Optional[str] = Field(None, max_length=100, description="常配送区域（如：上海-浦东）")

    @validator("car_no")
    def validate_car_no(cls, v):
        """
        车牌号校验
        :param v:
        :return:
        """
        if not v:
            raise ValueError("车牌号不能为空")
        # 标准化预处理
        v = v.strip().upper().replace(" ", "").replace("·", "")
        # 基础定义
        province = r"[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼]"
        engine = r"[A-HJ-NP-Z]"  # 排除 I, O
        common = r"[A-HJ-NP-Z0-9]"  # 排除 I, O

        # 车型
        # 1.普通货车/客车 (蓝牌/黄牌) - 7位
        # 格式：省份 + 字母 + 5位字符
        pattern_normal = f"^({province}){engine}{common}{{5}}$"

        # 2.挂车 (物流高频) - 8位
        # 格式：省份 + 字母 + 5位字符 + 挂
        pattern_trailer = f"^({province}){engine}{common}{{5}}挂$"

        # 3.小型新能源物流车 (渐变绿) - 8位
        # 格式：省份 + 字母 + D/F + 5位字符
        pattern_small_ev = f"^({province}){engine}[DF]{common}{{5}}$"

        # 4. 大型新能源货车/重卡 (黄绿双拼) - 8位
        # 格式：省份 + 字母 + 5位字符 + D/F
        pattern_large_ev = f"^({province}){engine}{common}{{5}}[DF]$"

        patterns = [pattern_normal, pattern_trailer, pattern_small_ev, pattern_large_ev]
        for pattern in patterns:
            if re.match(pattern, v):
                return v
        else:
            raise ValueError("车牌号格式错误")


class DriverExtCreateRequest(DriverExtBase):
    """
    创建司机扩展信息请求
    """
    pass


class DriverExtUpdateRequest(DriverExtBase):
    """
    修改司机扩展信息请求
    """
    id: int = Field(..., description="扩展ID")


class DriverExtResponse(BaseModel):
    """
    司机扩展信息响应
    """
    id: int
    user_id: int
    username: Optional[str] = Field(None, description="司机用户名")
    real_name: Optional[str] = Field(None, description="司机真实姓名")
    car_no: Optional[str]
    delivery_area: Optional[str]
    task_count: int = Field(0, description="待完成任务数")
    efficiency: float = Field(0.0, description="配送效率（完成率）")

    class Config:
        from_attributes = True


# 配送任务模型
class DeliveryTaskCreateRequest(BaseModel):
    """
    创建配送任务（订单分配）请求
    """
    order_id: int = Field(..., description="关联订单ID")
    driver_id: int = Field(..., description="分配司机ID")
    delivery_notes: Optional[str] = Field(None, max_length=200, description="配送备注")


class DeliveryTaskUpdateStatusRequest(BaseModel):
    """
    更新任务状态请求
    """
    task_id: int = Field(..., description="任务ID")
    task_status: TaskStatus = Field(..., description="任务状态")
    track_node: TrackStatus = Field(..., description="轨迹节点（仅状态变更时填写）")
    track_address: Optional[str] = Field(None, max_length=200, description="轨迹地址")


class DeliveryTaskResponse(BaseModel):
    """
    配送任务响应
    """
    id: int
    order_id: int
    order_no: Optional[str] = Field(None, description="订单号")
    driver_id: int
    driver_name: Optional[str] = Field(None, description="司机姓名")
    task_status: str
    assign_time: str
    assign_user_name: Optional[str] = Field(None, description="分配人名称")
    complete_time: Optional[str] = Field(None, description="完成时间")
    delivery_notes: Optional[str] = Field(None, description="配送备注")

    class Config:
        from_attributes = True


# 配送轨迹模型
class DeliveryTrackCreateRequest(BaseModel):
    """
    创建轨迹记录请求
    """
    task_id: int = Field(..., description="关联任务ID")
    track_node: TrackStatus = Field("已取货", description="轨迹节点（如：已取货/到达配送点）")
    track_address: str = Field(None, max_length=200, description="轨迹地址")


class DeliveryTrackResponse(BaseModel):
    """
    配送轨迹响应
    """
    id: int
    task_id: int
    track_node: str
    track_time: str
    track_address: Optional[str] = Field(None, description="轨迹地址")
    driver_name: Optional[str] = Field(None, description="操作司机姓名")

    class Config:
        from_attributes = True


# 任务查询模型
class DeliveryTaskQueryRequest(BaseModel):
    """
    配送任务查询请求
    """
    driver_id: Optional[int] = Field(None, description="司机ID")
    task_status: Optional[TaskStatus] = Field(None, description="任务状态")
    order_no: Optional[str] = Field(None, description="订单号")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=50, description="每页数量")
