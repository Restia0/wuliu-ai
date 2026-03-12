from dao.delivery_dao import delivery_dao
from models.schema.delivery_schema import (
    DriverExtCreateRequest, DriverExtUpdateRequest,
    DeliveryTaskCreateRequest, DeliveryTaskUpdateStatusRequest,
    DeliveryTrackCreateRequest, DeliveryTaskQueryRequest
)
from typing import Optional, List


class DeliveryService:
    def create_driver_ext(self, request: DriverExtCreateRequest) -> dict:
        """
        创建司机扩展信息（仅管理员）
        :param request:
        :return:
        """
        ext_dict = request.dict()
        ext_data = delivery_dao.create_driver_ext(ext_dict)
        return ext_data

    def update_driver_ext(self, request: DriverExtUpdateRequest) -> dict:
        """
        修改司机扩展信息（仅管理员/司机本人）
        :param request:
        :return:
        """
        ext_dict = request.dict()
        ext_data = delivery_dao.update_driver_ext(ext_dict)
        return ext_data

    def get_driver_ext(self, user_id: int) -> Optional[dict]:
        """
        查询司机扩展信息
        :param user_id:
        :return:
        """
        ext_data = delivery_dao.get_driver_ext(user_id)
        return ext_data

    def assign_delivery_task(self, request: DeliveryTaskCreateRequest, user_id: int) -> dict:
        """
        分配配送任务（仅管理员）
        :param request:
        :param user_id:
        :return:
        """
        task_data = request.dict()
        task_dict = delivery_dao.create_delivery_task(task_data, user_id)
        return task_dict

    def update_task_status(self, request: DeliveryTaskUpdateStatusRequest, driver_id: int) -> Optional[dict]:
        """
        更新任务状态（司机/管理员）
        :param driver_id:操作司机ID
        :param request:状态更新请求
        :return:更新后的任务信息
        """
        track_data = None
        if request.track_node:
            track_data = {
                "task_id": request.task_id,
                "track_node": request.track_node,
                "track_address": request.track_address,
                "driver_id": driver_id
            }
        track_dict = delivery_dao.update_task_status(request.task_id, request.task_status, track_data)
        return track_dict

    def get_delivery_task(self, task_id: int) -> Optional[dict]:
        """
        任务id查询任务信息
        :param task_id:
        :return:
        """
        task_dict = delivery_dao.get_delivery_task(task_id)
        return task_dict

    def query_delivery_tasks(self, request: DeliveryTaskQueryRequest, current_user: dict) -> dict:
        """
        查询配送任务
        :param request:
        :param current_user:
        :return:
        """
        query_params = request.dict()
        user_role = current_user.get("role")
        user_id = current_user.get("id")

        if user_role == "driver":
            # 司机仅查自己的任务
            query_params["driver_id"] = user_id

        task = delivery_dao.query_delivery_tasks(query_params)
        return task

    def create_delivery_track(self, request: DeliveryTrackCreateRequest, driver_id: int) -> dict:
        """
        创建配送轨迹
        :param request:
        :param driver_id:
        :return:
        """
        track_data = request.dict()
        track_data["driver_id"] = driver_id
        track_dict = delivery_dao.create_delivery_track(track_data)
        return track_dict

    def get_task_track(self, task_id: int) -> List[dict]:
        """
        查询任务轨迹（权限控制）
        - 管理员：可查所有轨迹
        - 司机：仅查自己的任务轨迹
        :param task_id:
        :return:
        """
        tracks = delivery_dao.get_task_track(task_id)
        return tracks

    # def calculate_driver_efficiency(self, user_id: int, days: int) -> float:
    #     """
    #     计算司机配送效率（仅管理员）
    #     :param user_id:
    #     :param days:
    #     :return:
    #     """
    #     efficiency = delivery_dao.calculate_driver_efficiency(user_id, days)
    #     return efficiency

    def batch_update_efficiency(self, days: int) -> None:
        """批量更新所有司机效率"""
        delivery_dao.batch_update_efficiency(days)



delivery_service = DeliveryService()
