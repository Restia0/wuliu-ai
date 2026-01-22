from dao.order_dao import order_dao
from models.schema.order_schema import (
    OrderCreateRequest, OrderStatusUpdateRequest, OrderQueryRequest
)
from dao.user_dao import user_dao
from typing import Dict, Optional, List


class OrderService:
    def create_order(self, order_request: OrderCreateRequest, create_user_id: int) -> dict:
        """
        创建订单（关联创建人ID）
        :param order_request:
        :param create_user_id:
        :return:
        """
        # 转换为字典
        order_data = order_request.dict(exclude_unset=True)
        # 补充创建人ID（从token获取）
        order_data["create_user_id"] = create_user_id
        # 创建订单
        order_dict = order_dao.create_order(order_data)
        return order_dict

    def get_order_detail(self, order_id: int, current_user: dict) -> dict | None:
        """
        查询订单详情（权限控制）：
        - 管理员：可查所有订单
        - 司机：仅查自己的订单
        - 普通用户：仅查自己创建的订单
        :param order_id:
        :param current_user:
        :return:
        """
        order_dict = order_dao.get_order_by_id(order_id)
        if not order_dict:
            return None

        # 权限校验
        user_role = current_user["role"]
        user_id = current_user["id"]

        if user_role == "admin":
            # 管理员无限制
            return order_dict
        elif user_role == "driver":
            # 司机仅查自己的订单（driver_id匹配）
            if order_dict["driver_id"] != user_id:
                return None
        else:
            # 普通用户仅查自己创建的订单（create_user_id匹配）
            if order_dict["create_user_id"] != user_id:
                return None

        return order_dict

    def query_orders(self, query_request: OrderQueryRequest, current_user: dict) -> Dict:
        """
        分页查询订单（权限控制）
        :param query_request:
        :param current_user:
        :return:
        """
        query_params = query_request.dict()
        user_role = current_user["role"]
        user_id = current_user["id"]

        # 权限过滤
        if user_role == "driver":
            # 司机仅查自己的订单
            query_params["driver_id"] = user_id
        elif user_role != "admin":
            # 普通用户仅查自己创建的订单（create_user_id筛选）
            query_params["create_user_id"] = user_id

        # 查询订单
        result = order_dao.query_orders(query_params)
        return result

    def update_order_status(self, order_id: int, current_user: dict,
                            status_request: OrderStatusUpdateRequest) -> dict | None:
        """
        修改订单状态（仅管理员可操作）
        :param order_id:
        :param current_user:
        :param status_request:
        :return:
        """
        # 权限校验：仅管理员可修改订单状态
        if current_user["role"] != "admin":
            return None

        # 转换为字典
        update_data = status_request.dict(exclude_unset=True)
        # 状态转换校验
        valid_status_transitions = {
            "pending": ["delivering", "cancelled"],
            "delivering": ["signed", "cancelled"],
            "signed": [],  # 已签收不可修改
            "cancelled": [],  # 已取消不可修改
        }

        # 获取原订单状态
        original_order = order_dao.get_order_by_id(order_id)
        if not original_order:
            return None
        original_status = original_order["order_status"]

        # 校验状态流转是否合法
        if update_data["order_status"] not in valid_status_transitions.get(original_status, []):
            raise ValueError(f"订单状态不能从{original_status}改为{update_data['order_status']}")

        # 修改状态
        order_dict = order_dao.update_order_status(order_id, update_data)
        return order_dict


# 创建Service实例
order_service = OrderService()
