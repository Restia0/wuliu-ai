from models.db_model.ai_model.ai_ocr_record import AIOcrRecord
from config.database import BaseDAO, db_session
from dao.order_dao import order_dao
from models.db_model.core_order import CoreOrder
from typing import Dict, Any, Optional

from utils.common_utils import logger
from utils.ocr_utils import pdf_to_text, extract_order_info_with_llm
from utils.warehouse_utils import match_warehouse_by_address


class OcrDao(BaseDAO):
    def __init__(self):
        super().__init__(AIOcrRecord)

    def create_ocr_record(self, record_date: dict) -> int:
        """
        创建OCR识别记录
        :param record_date:
        :return:
        """
        with db_session() as db:
            try:
                record = self.create(db, record_date)
                return record.id
            except Exception as e:
                logger.error(f"创建OCR记录失败：{str(e)}")
                raise ValueError(f"创建OCR记录失败：{str(e)}")

    def ocr_recognize_and_create_order(self, file_path: str, create_user_id: int) -> Dict[str, Any]:
        """
        核心流程：PDF OCR识别 → 大模型提取信息 → 自动创建订单
        :param file_path: PDF文件路径
        :param create_user_id: 操作人ID
        :return: 识别结果+订单信息
        """
        # 步骤1：PDF转文本（OCR识别）
        ocr_text = pdf_to_text(file_path)
        if not ocr_text:
            raise ValueError("OCR识别失败")

        # 步骤2：模型提取订单信息
        extract_result = extract_order_info_with_llm(ocr_text)
        result_data = extract_result["data"]

        # 步骤3：创建OCR记录（先记录，再创建订单）
        ocr_record_id = self.create_ocr_record({
            "ocr_image_url": file_path,
            "ocr_text": ocr_text,
            "extract_result": extract_result,
            "create_user_id": create_user_id
        })

        # 步骤4：自动创建订单（核心字段非空时）
        order_id = None
        required_fields = ["sender_name", "sender_phone", "receiver_name", "receiver_phone"]
        if all(result_data.get(field) for field in required_fields):
            # 组装订单数据
            order_data = {
                "sender_name": result_data["sender_name"],
                "sender_phone": result_data["sender_phone"],
                "sender_province": result_data["sender_province"],
                "sender_city": result_data["sender_city"],
                "sender_district": result_data["sender_district"],
                "sender_address": result_data["sender_address"],
                "receiver_name": result_data["receiver_name"],
                "receiver_phone": result_data["receiver_phone"],
                "receiver_province": result_data["receiver_province"],
                "receiver_city": result_data["receiver_city"],
                "receiver_district": result_data["receiver_district"],
                "receiver_address": result_data["receiver_address"],
                "goods_type": result_data["goods_type"],
                "goods_quantity": result_data["goods_quantity"],
                "create_user_id": create_user_id,
                "order_status": "pending"
            }

            # 自动匹配仓库ID（复用订单模块逻辑）
            province = order_data.get("sender_province")
            city = order_data.get("sender_city")
            warehouse_id = match_warehouse_by_address(province, city)
            order_data.setdefault("warehouse_id", warehouse_id)

            # 创建订单
            order_dict = order_dao.create_order(order_data)
            order_id = order_dict["id"]

            # 更新OCR记录关联的订单ID
            with db_session() as db:
                record = self.update(db, ocr_record_id, {"order_id": order_id})

            message = "OCR识别成功，已自动创建订单"

        else:
            message = "OCR识别成功，核心字段缺失，未创建订单"

        # 返回结果
        return {
            "ocr_record_id": ocr_record_id,
            "ocr_text": ocr_text,
            "extract_result": extract_result,
            "order_id": order_id,
            "message": message
        }

    def get_ocr_record_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        查询OCR识别记录详情
        :param record_id:
        :return:
        """
        with db_session() as db:
            record = self.get_by_id(db, record_id)
            if not record:
                return None

            record_dict = record.to_dict()
            return record_dict


# 创建DAO实例
ocr_dao = OcrDao()
