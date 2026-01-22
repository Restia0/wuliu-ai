from models.db_model.core_order import CoreOrder
from config.database import BaseDAO, db_session
from utils.order_utils import generate_order_no
from sqlalchemy import and_, or_
from typing import List, Dict, Optional


class OrderDAO(BaseDAO):
    def __init__(self):
        super().__init__(CoreOrder)

    def create_order(self, order_data: dict) -> dict:
        """
        创建订单（自动生成订单号）
        :param order_data:
        :return:
        """
        # 补充默认值
        order_data.setdefault("order_no", generate_order_no())
        order_data.setdefault("order_status", "pending")
        order_data.setdefault("is_delete", 0)
        # TODO
        order_data["warehouse_id"] = 1  # 先默认为1号仓库，后期在仓库模块时修改为自动匹配同城市仓库

        with db_session() as db:
            try:
                order = self.create(db, order_data)
                order_dict = self._order_to_dict(order)
                return order_dict
            except Exception as e:
                # 订单号重复
                raise ValueError(f"创建订单失败：{str(e)}")

    def get_order_by_id(self, order_id: int) -> dict | None:
        """
        根据ID查询订单
        :param order_id:
        :return:
        """
        with db_session() as db:
            order = self.get_by_conditions(db, {"id": order_id, "is_delete": 0})
            if not order:
                return None
            order_dict = self._order_to_dict(order)
            return order_dict

    def query_orders(self, query_params: dict) -> Dict:
        """
        分页查询订单
        query_params: {order_no, order_status, warehouse_id, driver_id, page, page_size}
        :param query_params:
        :return:
        """
        with db_session() as db:
            # 构建查询条件
            conditions = [CoreOrder.is_delete == 0]
            if query_params.get("order_no"):
                conditions.append(CoreOrder.order_no == query_params["order_no"])
            if query_params.get("order_status"):
                conditions.append(CoreOrder.order_status == query_params["order_status"])
            if query_params.get("warehouse_id"):
                conditions.append(CoreOrder.warehouse_id == query_params["warehouse_id"])
            if query_params.get("driver_id"):
                conditions.append(CoreOrder.driver_id == query_params["driver_id"])
            if query_params.get("create_user_id"):
                conditions.append(CoreOrder.create_user_id == query_params["create_user_id"])

            # 分页查询
            page = query_params.get("page", 1)
            page_size = query_params.get("page_size", 10)
            offset = (page - 1) * page_size

            # 总条数
            total = db.query(CoreOrder).filter(and_(*conditions)).count()
            # 分页数据
            orders = db.query(CoreOrder).filter(and_(*conditions)).offset(offset).limit(page_size).all()

            # 转换为字典列表
            order_list = [self._order_to_dict(order) for order in orders]

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "data": order_list
            }

    def update_order_status(self, order_id: int, update_data: dict) -> dict | None:
        """
        修改订单状态（支持关联司机ID）
        :param order_id:
        :param update_data:
        :return:
        """
        with db_session() as db:
            order = self.get_by_conditions(db, {"id": order_id, "is_delete": 0})
            if not order:
                return None

            # 只更新允许修改的字段
            allowed_fields = ["order_status", "driver_id"]
            update_data = {k: v for k, v in update_data.items() if k in allowed_fields}

            order = self.update(db, order, update_data)
            order_dict = self._order_to_dict(order)
            return order_dict

    def _order_to_dict(self, order: CoreOrder) -> dict:
        """
        ORM对象转字典（统一格式）
        :param order:
        :return:
        """
        # 拼接完整地址
        sender_address = f"{order.sender_province or ''}{order.sender_city or ''}{order.sender_district or ''}{order.sender_address or ''}".strip()
        receiver_address = f"{order.receiver_province or ''}{order.receiver_city or ''}{order.receiver_district or ''}{order.receiver_address or ''}".strip()

        return {
            "id": order.id,
            "order_no": order.order_no,
            # 发件人信息
            "sender_name": order.sender_name,
            "sender_phone": order.sender_phone,
            "sender_address": sender_address,
            # 收件人信息
            "receiver_name": order.receiver_name,
            "receiver_phone": order.receiver_phone,
            "receiver_address": receiver_address,
            # 货物信息
            "goods_type": order.goods_type,
            "goods_quantity": order.goods_quantity,
            # 状态/关联信息
            "order_status": order.order_status,
            "driver_id": order.driver_id,
            "warehouse_id": order.warehouse_id,
            "create_user_id": order.create_user_id,
            # 时间信息
            "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S") if order.create_time else "",
            "update_time": order.update_time.strftime("%Y-%m-%d %H:%M:%S") if order.update_time else ""
        }


# 创建DAO实例
order_dao = OrderDAO()
