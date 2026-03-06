from models.db_model.core_inbound import CoreInbound
from models.db_model.core_outbound import CoreOutbound
from models.db_model.core_warehouse import CoreWarehouse
from config.database import BaseDAO, db_session
from sqlalchemy import and_, func
from typing import Optional


class WarehouseDAO(BaseDAO):
    def __init__(self):
        super().__init__(CoreWarehouse)

    def create_warehouse(self, warehouse_data: dict) -> dict:
        """
        创建仓库
        :param warehouse_data:
        :return:
        """
        warehouse_data.setdefault("current_stock", 0)
        warehouse_data.setdefault("is_delete", 0)

        with db_session() as db:
            try:
                warehouse = self.create(db, warehouse_data)
                warehouse_dict = warehouse.to_dict()
                return warehouse_dict
            except Exception as e:
                # 仓库编号重复
                raise ValueError(f"创建仓库失败：{str(e)}")

    def update_warehouse(self, warehouse_data: dict) -> Optional[dict]:
        """
        修改仓库信息
        :param warehouse_data:
        :return:
        """
        warehouse_id = warehouse_data.pop("id")
        with db_session() as db:
            warehouse = self.get_by_conditions(db, {"id": warehouse_id, "is_delete": 0})
            if not warehouse:
                return None
            warehouse = self.update(db, warehouse, warehouse_data)
            warehouse_dict = warehouse.to_dict()
            return warehouse_dict

    def get_warehouse_by_id(self, warehouse_id: int) -> Optional[dict]:
        """
        根据ID查询仓库
        :param warehouse_id:
        :return:
        """
        with db_session() as db:
            warehouse = self.get_by_conditions(db, {"id": warehouse_id, "is_delete": 0})
            if not warehouse:
                return None
            warehouse_dict = warehouse.to_dict()
            return warehouse_dict

    def get_all_valid_warehouses(self) -> list[dict]:
        """
        获取所有有效仓库（未删除）
        :return:
        """
        with db_session() as db:
            warehouses = self.list_by_conditions(db, {"is_delete": 0})
            warehouse_list = [warehouse.to_dict() for warehouse in warehouses]
            return warehouse_list

    def get_default_warehouse(self) -> Optional[dict]:
        """
        获取默认仓库（第一个有效仓库）
        :return:
        """
        warehouses = self.get_all_valid_warehouses()
        warehouse = warehouses[0] if warehouses else None
        return warehouse

    def query_warehouse_stock(self, query_params: dict) -> dict:
        """
        查询库存（支持预警筛选）
        :param query_params:{warehouse_id, warning_only, page, page_size}
        :return:
        """
        with db_session() as db:
            # 基础条件
            conditions = [CoreWarehouse.is_delete == 0]
            if query_params.get("warehouse_id"):
                conditions.append(CoreWarehouse.id == query_params["warehouse_id"])
            # 预警筛选：current_stock > 80% capacity_limit
            if query_params.get("warning_only"):
                conditions.append(CoreWarehouse.current_stock > CoreWarehouse.capacity_limit * 0.8)

            # 分页
            page = query_params.get("page", 1)
            page_size = query_params.get("page_size", 10)
            offset = (page - 1) * page_size

            # 总条数
            total = db.query(CoreWarehouse).fliter(and_(*conditions)).count()
            # 分页数据
            warehouse = db.query(CoreWarehouse).filter(and_(*conditions)).offset(offset).limit(page_size).all()

            # 处理预警标记
            result_data = []
            for w in warehouse:
                w_dict = w.to_dict()
                w_dict["stock_warning"] = w.current_stock > w.capacity_limit * 0.8
                result_data.append(w_dict)

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "data": result_data
            }

    def increase_stock(self, db: db_session, warehouse_id: int, quantity: int) -> bool:
        """
        增加库存（入库/订单预占）
        :param db:
        :param warehouse_id:
        :param quantity:
        :return:操作成功返回True，失败返回False
        """
        warehouse = self.get_by_conditions(db, {"id": warehouse_id, "is_delete": 0})
        if not warehouse:
            return False
        # 防爆仓校验
        if warehouse.current_stock + quantity > warehouse.capacity_limit:
            return False
        warehouse.current_stock += quantity
        return True

    def decrease_stock(self, db: db_session, warehouse_id: int, quantity: int) -> bool:
        """
        减少库存（出库）
        :param db:
        :param warehouse_id:
        :param quantity:
        :return:操作成功返回True，失败返回False
        """
        warehouse = self.get_by_conditions(db, {"id": warehouse_id, "is_delete": 0})
        if not warehouse or warehouse.current_stock < quantity:
            return False
        warehouse.current_stock -= quantity
        return True

    def create_inbound_record(self, inbound_data: dict, operator_id: int) -> dict:
        """
        创建入库记录并更新库存
        :param inbound_data:
        :param operator_id:
        :return:
        """
        inbound_data["operator_id"] = operator_id

        with db_session() as db:
            try:
                # 1. 创建入库记录
                inbound = CoreInbound(**inbound_data)
                db.add(inbound)
                db.flush()
                # 2. 增加库存
                success = self.increase_stock(db, inbound_data["warehouse_id"], inbound_data["goods_quantity"])
                if not success:
                    raise ValueError("库存不足")
                return inbound.to_dict()
            except Exception as e:
                raise ValueError(f"入库失败：{str(e)}")

    def create_outbound_record(self, outbound_data: dict, operator_id: int) -> dict:
        """
        创建出库记录并更新库存
        :param outbound_data:
        :param operator_id:
        :return:
        """
        outbound_data["operator_id"] = operator_id

        with db_session() as db:
            try:
                # 1. 校验库存
                warehouse_id = outbound_data["warehouse_id"]
                quantity = outbound_data["goods_quantity"]
                success = self.decrease_stock(db, warehouse_id, quantity)
                if not success:
                    raise ValueError("库存不足")
                # 2. 创建出库记录
                outbound = CoreOutbound(**outbound_data)
                db.add(outbound)
                db.flush()
                return outbound.to_dict()
            except Exception as e:
                raise ValueError(f"出库失败：{str(e)}")


# 创建DAO实例
warehouse_dao = WarehouseDAO()
