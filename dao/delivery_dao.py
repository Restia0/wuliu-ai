from models.db_model.core_delivery_task import CoreDeliveryTask
from models.db_model.core_delivery_track import CoreDeliveryTrack
from models.db_model.core_driver_ext import CoreDriverExt
from models.db_model.core_order import CoreOrder
from config.database import BaseDAO, db_session
from sqlalchemy import and_, or_, func
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dao.warehouse_dao import warehouse_dao
from dao.order_dao import order_dao
from dao.user_dao import user_dao


class DeliveryDAO(BaseDAO):
    def __init__(self):
        super().__init__(CoreDeliveryTask)

    def create_driver_ext(self, ext_data: dict) -> dict:
        """
        创建司机扩展信息
        :param ext_data:
        :return:
        """
        with db_session() as db:
            try:
                # 校验用户是否存在且角色为司机
                user = user_dao.get_user_by_id(ext_data["user_id"])
                if not user or user.get("role") != "driver":
                    raise ValueError("用户不存在或角色不是司机")

                ext = CoreDriverExt(**ext_data)
                db.add(ext)
                db.flush()
                ext_dict = self._driver_ext_to_dict(ext)
                return ext_dict
            except Exception as e:
                raise ValueError(f"创建司机扩展信息失败：{str(e)}")

    def update_driver_ext(self, ext_data: dict) -> dict:
        """
        修改司机扩展信息
        :param ext_data:
        :return:
        """
        ext_id = ext_data.pop("id")
        with db_session() as db:
            ext = db.query(CoreDriverExt).filter(CoreDriverExt.id == ext_id).first()
            if not ext:
                raise ValueError("司机扩展信息不存在")

            ext = self.update(db, ext, ext_data)
            ext_dict = self._driver_ext_to_dict(ext)
            return ext_dict

    def get_driver_ext(self, user_id: int) -> Optional[dict]:
        """
        根据用户ID查询司机扩展信息
        :param user_id:
        :return:
        """
        with db_session() as db:
            ext = db.query(CoreDriverExt).filter(CoreDriverExt.user_id == user_id).first()
            if not ext:
                return None
            ext_dict = self._driver_ext_to_dict(ext)
            return ext_dict

    def create_delivery_task(self, task_data: dict, assign_user_id: int) -> dict:
        """
        创建配送任务（订单分配）
        联动逻辑：
        1. 更新订单状态为delivering + 关联司机ID
        2. 调用仓库出库接口，减少库存
        3. 增加司机待完成任务数
        :param task_data:
        :param assign_user_id:
        :return:
        """
        with (db_session() as db):
            try:
                # 1. 校验订单状态（仅pending状态可分配）
                order = db.query(CoreOrder).filter(and_(
                    CoreOrder.id == task_data["order_id"],
                    CoreOrder.order_status == "pending",
                    CoreOrder.is_delete == 0)
                ).first()
                if not order:
                    raise ValueError("订单不存在或非待分配状态")

                # 2. 调用仓库出库接口（联动仓库模块）
                outbound_success = warehouse_dao.create_outbound_record({
                    "warehouse_id": order.warehouse_id,
                    "order_id": order.id,
                    "goods_type": order.goods_type,
                    "goods_quantity": order.goods_quantity
                }, assign_user_id)
                if not outbound_success:
                    raise ValueError("仓库出库失败")

                # 3.创建配送任务
                # 访问字典[]为直接访问，若不存在则会报错，get为安全访问，若不存在，则会返回None
                task = CoreDeliveryTask(
                    order_id=task_data["order_id"],
                    driver_id=task_data["driver_id"],
                    delivery_notes=task_data.get("delivery_notes"),
                    assign_user_id=assign_user_id
                )
                db.add(task)

                # 4.更新订单状态 + 关联司机ID
                order.order_status = "delivering"
                order.driver_id = task_data["driver_id"]

                # 5.增加司机待完成任务数
                self._update_driver_task_count(db, task_data["driver_id"], 1)

                db.flush()
                task_dict = self._delivery_task_to_dict(task)
                return task_dict
            except Exception as e:
                raise ValueError(f"创建配送任务失败：{str(e)}")

    def update_task_status(self, task_id: int, task_status: str, track_data: Optional[dict]) -> Optional[dict]:
        """
        更新任务状态
        联动逻辑：
        1. 完成任务时更新订单状态为signed + 记录完成时间
        2. 取消任务时更新订单状态为cancelled
        3. 新增轨迹记录
        4. 完成/取消任务时减少司机待完成任务数
        :param task_id:
        :param task_status:
        :param track_data:
        :return:
        """
        with db_session() as db:
            try:
                task = self.get_by_conditions(db, {"id": task_id})
                if not task:
                    return None

                # 1. 更新任务状态
                task.task_status = task_status

                # 2. 处理完成/取消状态
                if task_status == "completed":
                    task.complete_time = datetime.now()
                    # 更新订单状态为已签收
                    order = db.query(CoreOrder).filter(CoreOrder.id == task.order_id).first()
                    if order:
                        order.order_status = "signed"
                    # 减少司机待完成任务数
                    self._update_driver_task_count(db, task.driver_id, -1)
                    db.flush()
                    self.update_efficiency(db, task.driver_id)

                elif task_status == "cancelled":
                    # 更新订单状态为已取消
                    order = db.query(CoreOrder).filter(CoreOrder.id == task.order_id).first()
                    if order:
                        order.order_status = "cancelled"
                    # 减少司机待完成任务数
                    self._update_driver_task_count(db, task.driver_id, -1)
                    db.flush()

                # 3. 新增轨迹记录（如果传入轨迹信息）
                if track_data:
                    track = CoreDeliveryTrack(
                        task_id=task_id,
                        track_node=track_data.get("track_node"),
                        track_address=track_data.get("track_address"),
                        driver_id=task.driver_id
                    )
                    db.add(track)

                task_dict = self._delivery_task_to_dict(task)
                return task_dict
            except Exception as e:
                raise ValueError(f"更新任务状态失败：{str(e)}")

    def get_delivery_task(self, task_id: int) -> Optional[dict]:
        """
        任务id查询任务信息
        :param task_id:
        :return:
        """
        with db_session() as db:
            task = self.get_by_conditions(db, {"id": task_id})
            if not task:
                return None
            task_dict = self._delivery_task_to_dict(task)
            return task_dict

    def query_delivery_tasks(self, query_params: dict) -> dict:
        """
        分页查询配送任务
        :param query_params:
        :return:
        """
        with db_session() as db:
            # 构建查询条件
            conditions = []
            if query_params.get("driver_id"):
                conditions.append(CoreDeliveryTask.driver_id == query_params["driver_id"])
            if query_params.get("task_status"):
                conditions.append(CoreDeliveryTask.task_status == query_params["task_status"])

            # 关联订单表查询订单号
            if query_params.get("order_no"):
                conditions.append(CoreOrder.order_no == query_params["order_no"])

            # 分页
            page = query_params.get("page", 1)
            page_size = query_params.get("page_size", 10)
            offset = (page - 1) * page_size

            # 关联查询
            query = db.query(CoreDeliveryTask, CoreOrder).join(CoreOrder, CoreDeliveryTask.order_id == CoreOrder.id,
                                                               isouter=True)
            if conditions:
                query = query.filter(and_(*conditions))

            # 总条数
            total = query.count()
            # 分页数据
            task_list = query.offset(offset).limit(page_size).all()

            # 转换为字典
            result_data = []
            for task, order in task_list:
                task_dict = self._delivery_task_to_dict(task)
                if order:
                    task_dict["order_no"] = order.order_no
                result_data.append(task_dict)

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "data": result_data
            }

    def create_delivery_track(self, track_data: dict) -> dict:
        """
        创建配送轨迹记录
        :param track_data:
        :return:
        """
        with db_session() as db:
            try:
                task = self.get_by_conditions(db, {"id": track_data.get("task_id")})
                if not task:
                    raise ValueError("配送任务不存在")

                track = CoreDeliveryTrack(**track_data)
                db.add(track)
                db.flush()
                track_dict = self._delivery_track_to_dict(track)
                return track_dict
            except Exception as e:
                raise ValueError(f"创建轨迹记录失败：{str(e)}")

    def get_task_track(self, task_id: int) -> List[dict]:
        """
        根据任务ID查询轨迹记录
        :param task_id:
        :return:
        """
        with db_session() as db:
            tracks = db.query(CoreDeliveryTrack).filter(CoreDeliveryTrack.task_id == task_id).order_by(
                CoreDeliveryTrack.track_time.desc()).all()
            return [self._delivery_track_to_dict(track) for track in tracks]

    # 辅助方法，转dict
    def _driver_ext_to_dict(self, ext: CoreDriverExt) -> dict:
        """
        司机扩展信息转字典
        :param ext:
        :return:
        """
        # 关联用户信息
        user = user_dao.get_user_by_id(ext.user_id)
        return {
            "id": ext.id,
            "user_id": ext.user_id,
            "username": user.get("username") if user else None,
            "real_name": user.get("real_name") if user else None,
            "car_no": ext.car_no,
            "delivery_area": ext.delivery_area,
            "task_count": ext.task_count,
            "efficiency": round(ext.efficiency, 2) if ext.efficiency else 0.0
        }

    def _delivery_task_to_dict(self, task: CoreDeliveryTask) -> dict:
        """
        配送任务转字典
        :param task:
        :return:
        """
        # 关联分配人信息
        assign_user = user_dao.get_user_by_id(task.assign_user_id) if task.assign_user_id else None
        # 关联司机信息
        driver = user_dao.get_user_by_id(task.driver_id) if task.driver_id else None
        # 关联订单信息
        order = order_dao.get_order_by_id(task.order_id) if task.order_id else None

        return {
            "id": task.id,
            "order_id": task.order_id,
            "order_no": order.get("order_no") if order else None,
            "driver_id": task.driver_id,
            "driver_name": driver.get("real_name") if driver else None,
            "task_status": task.task_status,
            "assign_time": task.assign_time.strftime("%Y-%m-%d %H:%M:%S") if task.assign_time else None,
            "assign_user_name": assign_user.get("real_name") if assign_user else None,
            "complete_time": task.complete_time.strftime("%Y-%m-%d %H:%M:%S") if task.complete_time else None,
            "delivery_notes": task.delivery_notes,
        }

    def _delivery_track_to_dict(self, track: CoreDeliveryTrack) -> dict:
        """
        配送轨迹转字典
        :param track:
        :return:
        """
        # 关联司机信息
        driver = user_dao.get_user_by_id(track.driver_id) if track.driver_id else None
        return {
            "id": track.id,
            "task_id": track.task_id,
            "track_node": track.track_node,
            "track_time": track.track_time.strftime("%Y-%m-%d %H:%M:%S") if track.track_time else "",
            "track_address": track.track_address,
            "driver_name": driver.get("real_name") if driver else None
        }

    def _update_driver_task_count(self, db: db_session(), driver_id: int, count: int) -> None:
        """
        更新司机待完成任务数
        :param driver_id:
        :param count:
        :return:
        """
        ext = db.query(CoreDriverExt).filter(CoreDriverExt.user_id == driver_id).first()
        if ext:
            ext.task_count += count
            # 避免负数
            if ext.task_count < 0:
                ext.task_count = 0

    def calculate_driver_efficiency(self, db: db_session(), driver_id: int, days: int = 30) -> float:
        """
        计算司机配送效率（近N天）
        :param db:
        :param driver_id:司机用户ID
        :param days:统计天数，默认30天
        :return:配送效率（0-100，保留2位小数）
        """
        start_time = datetime.now() - timedelta(days=days)

        # 计算统计起始时间（近N天）
        total_task_sql = db.query(func.count(CoreDeliveryTask.id)).filter(
            and_(
                CoreDeliveryTask.driver_id == driver_id,
                CoreDeliveryTask.assign_time >= start_time
            )
        )
        total_task = total_task_sql.scalar() or 0

        # 2. 统计该司机近N天已完成任务数（排除取消的任务）
        completed_task_sql = db.query(func.count(CoreDeliveryTask.id)).filter(
            and_(
                CoreDeliveryTask.driver_id == driver_id,
                CoreDeliveryTask.assign_time >= start_time,
                CoreDeliveryTask.task_status == "completed"
            )
        )
        completed_task = completed_task_sql.scalar() or 0

        # 3. 计算效率（避免除以0）
        if total_task == 0:
            efficiency = 0.0
        else:
            efficiency = round((completed_task / total_task) * 100, 2)

        return efficiency

    def batch_update_efficiency(self, days: int = 30) -> None:
        """
        批量更新所有司机效率
        :param days:
        :return:
        """
        with db_session() as db:
            # 获取所有有效司机
            driver_ext = db.query(CoreDriverExt).all()
            for ext in driver_ext:
                efficiency = self.calculate_driver_efficiency(db, ext.user_id, days)
                ext.efficiency = efficiency

    def update_efficiency(self, db: db_session(), driver_id: int, days: int = 30) -> None:
        """更新单个司机效率"""
        efficiency = self.calculate_driver_efficiency(db, driver_id, days)
        driver_ext = db.query(CoreDriverExt).filter(CoreDriverExt.user_id == driver_id).first()
        if driver_ext:
            driver_ext.efficiency = efficiency

    def smart_assign_driver(self, order_id: int) -> Optional[int]:
        """
        智能分配最优司机
        :param order_id:司机ID
        :return:推荐的司机ID，无合适司机时返回None
        """
        with db_session() as db:
            # 1. 获取订单信息（重点：收件地址）
            order = db.query(CoreOrder).filter(CoreOrder.id == order_id).first()
            if not order:
                return None
            # 提取订单收件核心区域（如：上海市/广东省）
            order_receive_area = f"{order.receiver_province}-{order.receiver_city}"

            # 2. 获取所有有效司机（排除已删除、效率过低的）
            valid_drivers = db.query(CoreDriverExt).filter(
                and_(
                    CoreDriverExt.efficiency >= 60
                )
            ).all()
            if not valid_drivers:
                return None

            # 3. 算法核心：多维度排序
            driver_candidates = []
            for driver in valid_drivers:
                # 维度1：区域匹配度（0/1，核心权重）
                area_match = 1 if driver.delivery_area and order_receive_area in driver.delivery_area else 0
                # 维度2：待完成任务数（越小越优）
                task_count = driver.task_count
                # 维度3：效率（越大越优）
                efficiency = driver.efficiency

                driver_candidates.append({
                    "driver_id": driver.user_id,
                    "area_match": area_match,
                    "task_count": task_count,
                    "efficiency": efficiency
                })

            # 4. 排序规则：区域匹配→任务量升序→效率降序
            driver_candidates.sort(key=lambda x: (-x["area_match"], x["task_count"], -x["efficiency"]))

            return driver_candidates[0]["driver_id"] if driver_candidates else None


delivery_dao = DeliveryDAO()
