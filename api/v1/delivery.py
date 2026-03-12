from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from models.schema.delivery_schema import (
    DriverExtCreateRequest, DriverExtUpdateRequest, DriverExtResponse,
    DeliveryTaskCreateRequest, DeliveryTaskUpdateStatusRequest, DeliveryTaskResponse,
    DeliveryTrackCreateRequest, DeliveryTrackResponse,
    DeliveryTaskQueryRequest
)
from service.delivery_service import delivery_service
from utils.common_utils import logger

# 认证依赖
bearer_scheme = HTTPBearer(auto_error=False)
router = APIRouter()


@router.post("/driver/ext/create", summary="创建司机扩展信息", response_model=DriverExtResponse,
             dependencies=[Depends(bearer_scheme)])
def create_driver_ext(request: Request, ext_data: DriverExtCreateRequest):
    """
    创建司机扩展信息（仅管理员和司机）
    :param request:
    :param ext_data:
    :return:
    """
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限创建司机扩展信息")

    try:
        ext_dict = delivery_service.create_driver_ext(ext_data)
        logger.info(f"创建司机扩展信息成功：用户ID={ext_data.user_id}")
        return ext_dict
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"创建司机扩展信息失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建司机扩展信息失败")


@router.post("/driver/ext/update", summary="修改司机扩展信息", response_model=DriverExtResponse,
             dependencies=[Depends(bearer_scheme)])
def update_driver_ext(request: Request, ext_data: DriverExtUpdateRequest):
    """
    修改司机扩展信息（仅管理员/司机本人）
    :param request:
    :param ext_data:
    :return:
    """
    current_user_id = request.state.user_id
    current_role = request.state.role

    if current_role != "admin" and current_user_id != ext_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改司机扩展信息")

    ext_dict = delivery_service.update_driver_ext(ext_data)
    if not ext_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="司机扩展信息不存在")

    logger.info(f"修改司机扩展信息成功：用户ID={ext_data.id}")
    return ext_dict


@router.get("/driver/ext/{user_id}", summary="查询司机扩展信息", response_model=DriverExtResponse,
            dependencies=[Depends(bearer_scheme)])
def get_driver_ext(user_id: int):
    """
    查询司机扩展信息（登录用户均可查看）
    :param user_id:
    :return:
    """
    ext_dict = delivery_service.get_driver_ext(user_id)
    if not ext_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="司机扩展信息不存在")
    return ext_dict


@router.post("/task/assign", summary="创建配送任务", response_model=DeliveryTaskResponse,
             dependencies=[Depends(bearer_scheme)])
def assign_delivery_task(request: Request, task_data: DeliveryTaskCreateRequest):
    """
    分配配送任务（仅管理员）
    :param request:
    :param task_data:
    :return:
    """
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限分配配送任务")

    try:
        task_dict = delivery_service.assign_delivery_task(task_data, request.state.user_id)
        logger.info(f"分配配送任务成功：订单ID={task_data.order_id} → 司机ID={task_data.driver_id}")
        return task_dict
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"分配配送任务失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="分配配送任务失败")


@router.post("/task/status", summary="更新任务状态", response_model=DeliveryTaskResponse,
             dependencies=[Depends(bearer_scheme)])
def update_task_status(request: Request, status_data: DeliveryTaskUpdateStatusRequest):
    """
    更新任务状态（管理员/司机本人）
    :param request:
    :param status_data:
    :return:
    """
    current_user_id = request.state.user_id
    current_role = request.state.role

    # 权限校验：管理员 或 任务所属司机
    if current_role != "admin":
        task = delivery_service.get_delivery_task(status_data.task_id)
        if not task or task.get("driver_id") != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限更新任务状态")

    try:
        task_dict = delivery_service.update_task_status(status_data, current_user_id)
        if not task_dict:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

        logger.info(f"更新任务状态成功：任务ID={status_data.task_id} → 状态={status_data.task_status}")
        return task_dict
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"更新任务状态失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新任务状态失败")


@router.post("/task/query", summary="查询配送任务", dependencies=[Depends(bearer_scheme)])
def query_delivery_tasks(request: Request, query_data: DeliveryTaskQueryRequest = Depends()):
    """
    查询配送任务（带权限控制）
    :param request:
    :param query_data:
    :return:
    """
    try:
        current_user = {
            "id": request.state.user_id,
            "role": request.state.role
        }
        result = delivery_service.query_delivery_tasks(query_data, current_user)
        return result
    except Exception as e:
        logger.error(f"查询配送任务失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="查询配送任务失败")


@router.post("/track/create", summary="创建配送轨迹", response_model=DeliveryTrackResponse,
             dependencies=[Depends(bearer_scheme)])
def create_delivery_track(request: Request, track_data: DeliveryTrackCreateRequest):
    """
    创建配送轨迹 仅任务所属司机可以
    :param request:
    :param track_data:
    :return:
    """
    current_user_id = request.state.user_id

    # 校验是否为任务所属司机
    task = delivery_service.get_delivery_task(track_data.task_id)
    if not task or task.get("driver_id") != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限创建配送轨迹")

    try:
        track_dict = delivery_service.create_delivery_track(track_data, current_user_id)
        logger.info(f"创建轨迹记录成功：任务ID={track_data.task_id} → 节点={track_data.track_node}")
        return track_dict
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"创建配送轨迹失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建配送轨迹失败")


@router.get("/track/{task_id}", summary="查询配送轨迹", dependencies=[Depends(bearer_scheme)])
def get_task_track(task_id: int, request: Request):
    """
    查询任务轨迹（带权限控制）
    - 管理员：可查所有轨迹
    - 司机：仅查自己的任务轨迹
    :param task_id:
    :param request:
    :return:
    """
    user_role = request.state.role
    user_id = request.state.user_id

    # 校验权限
    if user_role != "admin":
        # 司机仅查自己的任务轨迹
        task = delivery_service.get_delivery_task(task_id)
        if not task or task.get("driver_id") != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限查询配送轨迹")

    tracks = delivery_service.get_task_track(task_id)
    return {
        "task_id": task_id,
        "tracks": tracks
    }


# @router.get("/driver/efficiency/{user_id}", summary="计算司机效率", dependencies=[Depends(bearer_scheme)])
# def calculate_driver_efficiency(user_id: int, days: int = 30):
#     """
#     计算司机配送效率（仅管理员）
#     :param user_id:
#     :param days:
#     :return:
#     """
#     try:
#         efficiency = delivery_service.calculate_driver_efficiency(user_id, days)
#         return {
#             "driver_id": user_id,
#             "stat_days": days,
#             "efficiency": efficiency
#         }
#     except Exception as e:
#         logger.error(f"计算司机效率失败：{str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="计算司机效率失败")

# 批量更新所有司机效率（定时任务接口）
@router.post("/driver/efficiency/batch", summary="批量更新所有司机效率", dependencies=[Depends(bearer_scheme)])
def batch_update_efficiency(request: Request, days: int = 30):
    """批量更新所有司机效率"""
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可批量更新司机效率")
    try:
        delivery_service.batch_update_efficiency(days)
        return {"message": f"批量更新所有司机效率完成（统计近{days}天）"}
    except Exception as e:
        logger.error(f"批量更新司机效率失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="批量更新司机效率失败")

