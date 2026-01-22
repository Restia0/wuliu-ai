from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from models.schema.order_schema import (
    OrderCreateRequest, OrderStatusUpdateRequest, OrderQueryRequest,
    OrderDetailResponse, OrderListResponse
)
from service.order_service import order_service
from utils.common_utils import logger

# HTTPBearer认证依赖
bearer_scheme = HTTPBearer(auto_error=False)

# 创建路由实例
router = APIRouter()


@router.post("/create", summary="创建订单", response_model=OrderDetailResponse, dependencies=[Depends(bearer_scheme)])
def create_order(request: Request, order_data: OrderCreateRequest):
    """
    创建订单（登录用户均可创建）
    :param request:
    :param order_data:
    :return:
    """
    try:
        # 获取当前登录用户ID
        current_user_id = request.state.user_id
        order_dict = order_service.create_order(order_data, current_user_id)
        logger.info(f"订单创建成功：{order_dict['order_no']}（创建人：{current_user_id}）")
        return order_dict
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"创建订单失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建订单失败")


@router.get("/detail/{order_id}", summary="查询订单详情", response_model=OrderDetailResponse,
            dependencies=[Depends(bearer_scheme)])
def get_order_detail(order_id: int, request: Request):
    """
    查询订单详情（带权限控制）
    :param order_id:
    :param request:
    :return:
    """
    # 构建当前用户信息
    current_user = {
        "id": request.state.user_id,
        "role": request.state.role,
        "username": request.state.username
    }

    order_dict = order_service.get_order_detail(order_id, current_user)
    if not order_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在或无权限查看")
    return order_dict


@router.get("/query", summary="分页查询订单", response_model=OrderListResponse, dependencies=[Depends(bearer_scheme)])
def query_orders(request: Request, query_data: OrderQueryRequest = Depends()):
    """
    分页查询订单（带权限控制）
    :param request:
    :param query_data:
    :return:
    """
    try:
        current_user = {
            "id": request.state.user_id,
            "role": request.state.role,
            "username": request.state.username
        }
        result = order_service.query_orders(query_data, current_user)
        return result
    except ValueError as e:
        logger.error(f"查询订单失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="查询订单失败")


@router.put("/status/{order_id}", summary="修改订单状态", response_model=OrderDetailResponse,
            dependencies=[Depends(bearer_scheme)])
def update_order_status(order_id: int, request: Request, status_data: OrderStatusUpdateRequest):
    """
    修改订单状态（仅管理员可操作）
    :param order_id:
    :param request:
    :param status_data:
    :return:
    """
    current_user = {
        "id": request.state.user_id,
        "role": request.state.role,
        "username": request.state.username
    }

    order_dict = order_service.update_order_status(order_id, current_user, status_data)

    if not order_dict:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改订单状态或订单不存在")

    logger.info(f"订单状态修改成功：{order_dict['order_no']} → {status_data.order_status}")
    return order_dict

