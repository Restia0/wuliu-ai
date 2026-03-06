from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from models.schema.warehouse_schema import (
    WarehouseCreateRequest, WarehouseUpdateRequest, WarehouseDetailResponse,
    WarehouseListResponse, InboundRequest, OutboundRequest,
    StockQueryRequest, StockRecordResponse
)
from service.warehouse_service import warehouse_service
from utils.common_utils import logger

# HTTPBearer认证依赖
bearer_scheme = HTTPBearer(auto_error=False)

# 创建路由实例
router = APIRouter()


# 仓库基础信息管理
@router.post("/create", summary="创建仓库", response_model=WarehouseDetailResponse,
             dependencies=[Depends(bearer_scheme)])
def create_warehouse(request: Request, warehouse_data: WarehouseCreateRequest):
    """
    创建仓库（仅管理员）
    :param request:
    :param warehouse_data:
    :return:
    """
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可创建仓库")

    try:
        warehouse_dict = warehouse_service.create_warehouse(warehouse_data)
        logger.info(f"仓库创建成功：{warehouse_dict['warehouse_name']}（ID：{warehouse_dict['id']}）")
        return warehouse_dict
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"创建仓库失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建仓库失败")


@router.post("/update", summary="修改仓库信息", response_model=WarehouseDetailResponse,
             dependencies=[Depends(bearer_scheme)])
def update_warehouse(request: Request, warehouse_data: WarehouseUpdateRequest):
    """
    修改仓库信息（仅管理员）
    :param request:
    :param warehouse_data:
    :return:
    """
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可修改仓库信息")

    warehouse_dict = warehouse_service.update_warehouse(warehouse_data)
    if not warehouse_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="仓库不存在")

    logger.info(f"仓库修改成功：{warehouse_dict['warehouse_name']}（ID：{warehouse_dict['id']}）")
    return warehouse_dict


@router.get("/detail/{warehouse_id}", summary="查询仓库详情", response_model=WarehouseDetailResponse,
            dependencies=[Depends(bearer_scheme)])
def get_warehouse_detail(warehouse_id: int):
    """
     查询仓库详情（登录用户均可查看）
     :param warehouse_id:
     :return:
     """
    warehouse_dict = warehouse_service.get_warehouse_detail(warehouse_id)
    if not warehouse_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="仓库不存在")
    return warehouse_dict


@router.post("/stock/query", summary="库存查询（支持预警筛选）", response_model=WarehouseListResponse,
             dependencies=[Depends(bearer_scheme)])
def query_stock(query_data: StockQueryRequest = Depends()):
    """
    库存查询（登录用户均可查看）
    :param query_data:
    :return:
    """
    try:
        result = warehouse_service.query_stock(query_data)
        return result
    except Exception as e:
        logger.error(f"库存查询失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="库存查询失败")


@router.post("/inbound", summary="入库操作", response_model=StockRecordResponse,
             dependencies=[Depends(bearer_scheme)])
def inbound(request: Request, inbound_data: InboundRequest):
    """
    入库操作（仅管理员）
    :param request:
    :param inbound_data:
    :return:
    """
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可执行入库操作")

    try:
        record = warehouse_service.inbound(inbound_data, request.state.user_id)
        logger.info(f"入库操作成功：仓库ID={inbound_data.warehouse_id}，数量={inbound_data.goods_quantity}")
        return record
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"入库操作失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="入库操作失败")


@router.post("/outbound", summary="出库操作", response_model=StockRecordResponse,
             dependencies=[Depends(bearer_scheme)])
def outbound(request: Request, outbound_data: OutboundRequest):
    """
    出库操作（仅管理员）
    :param request:
    :param outbound_data:
    :return:
    """
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可执行出库操作")

    try:
        record = warehouse_service.outbound(outbound_data, request.state.user_id)
        logger.info(f"出库操作成功：仓库ID={outbound_data.warehouse_id}，订单ID={outbound_data.order_id}，数量={outbound_data.goods_quantity}")
        return record
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"出库操作失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="出库操作失败")
