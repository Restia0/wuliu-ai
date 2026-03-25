import os

from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File
from fastapi.security import HTTPBearer

from models.schema.ocr_schema import OcrRecognitionResponse, OcrRecognitionRequest
from service.ocr_service import ocr_service
from utils.common_utils import logger

# 认证依赖
bearer_scheme = HTTPBearer(auto_error=False)
router = APIRouter()

# 文件上传临时目录（需提前创建）
UPLOAD_DIR = "./uploads/ocr_pdf"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/recognize", summary="PDF OCR识别并创建订单", response_model=OcrRecognitionResponse,
             dependencies=[Depends(bearer_scheme)])
async def ocr_recognize(request: Request, file: UploadFile = File(...)):
    """
    上传PDF文件，OCR识别并自动创建订单
    :param request: 请求对象
    :param file: PDF文件
    :return: 识别结果
    """
    # 1. 权限校验（仅管理员）
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    # 2. 保存上传文件
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        logger.error(f"保存上传文件失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"文件保存失败：{str(e)}")

    # 3. 调用OCR服务
    try:
        ocr_request = OcrRecognitionRequest(file_path=file_path, create_user_id=request.state.user_id)
        result = ocr_service.ocr_recognize(ocr_request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"OCR识别失败：{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OCR识别失败")


@router.get("/record/{record_id}", summary="查询OCR识别记录", dependencies=[Depends(bearer_scheme)])
def get_ocr_record(record_id: int):
    """查询OCR识别记录详情"""
    record = ocr_service.get_ocr_record(record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OCR识别记录不存在")
    return record
