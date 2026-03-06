from dao.warehouse_dao import warehouse_dao
from models.schema.warehouse_schema import (
    WarehouseCreateRequest, WarehouseUpdateRequest, InboundRequest,
    OutboundRequest, StockQueryRequest
)
from typing import Dict, Optional, List


class WarehouseService:
    def create_warehouse(self, warehouse_request: WarehouseCreateRequest) -> dict:
        """
        创建仓库（仅管理员）
        :param warehouse_request:
        :return:
        """
        warehouse_data = warehouse_request.dict(exclude_unset=True)
        warehouse_dict = warehouse_dao.create_warehouse(warehouse_data)
        return warehouse_dict

    def update_warehouse(self, warehouse_request: WarehouseUpdateRequest) -> Optional[dict]:
        """
        修改仓库信息（仅管理员）
        :param warehouse_request:
        :return:
        """
        warehouse_date = warehouse_request.dict()
        warehouse_dict = warehouse_dao.update_warehouse(warehouse_date)
        return warehouse_dict

    def get_warehouse_detail(self, warehouse_id: int) -> Optional[dict]:
        """
        查询仓库详情
        :param warehouse_id:
        :return:
        """
        warehouse_dict = warehouse_dao.get_warehouse_by_id(warehouse_id)
        return warehouse_dict

    def query_stock(self, query_request: StockQueryRequest) -> dict:
        """
        查询库存（支持预警筛选）
        :param query_request:
        :return:
        """
        query_params = query_request.dict()
        result = warehouse_dao.query_warehouse_stock(query_params)
        return result

    def inbound(self, inbound_request: InboundRequest, operator_id: int) -> dict:
        """
        入库操作（仅管理员）
        :param inbound_request:
        :param operator_id:
        :return:
        """
        inbound_data = inbound_request.dict()
        result = warehouse_dao.create_inbound_record(inbound_data, operator_id)
        return result

    def outbound(self, outbound_request: OutboundRequest, operator_id: int) -> dict:
        """
        出库操作（仅管理员）
        :param outbound_request:
        :param operator_id:
        :return:
        """
        outbound_data = outbound_request.dict()
        result = warehouse_dao.create_outbound_record(outbound_data, operator_id)
        return result


# 创建Service实例
warehouse_service = WarehouseService()
