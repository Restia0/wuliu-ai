from models.schema.ocr_schema import OcrRecognitionRequest, OrderExtractResult
from dao.ocr_dao import ocr_dao
from typing import Dict, Any, Optional

from utils.common_utils import logger


class OcrService:
    def ocr_recognize(self, request: OcrRecognitionRequest) -> Dict[str, Any]:
        """
        OCR识别并尝试创建订单
        :param request: OCR识别请求
        :return: 识别结果
        """
        # 1. 调用DAO层核心方法
        result = ocr_dao.ocr_recognize_and_create_order(
            file_path=request.file_path,
            create_user_id=request.create_user_id
        )

        # 2. 校验提取结果（数据合法性）
        try:
            extract_result = OrderExtractResult(**result["extract_result"]["data"])
            result["extract_result"]["data"] = extract_result.dict()
        except Exception as e:
            logger.warning(f"提取结果校验警告：{str(e)}")

        return result

    def get_ocr_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        """查询OCR识别记录"""
        return ocr_dao.get_ocr_record_by_id(record_id)


ocr_service = OcrService()
