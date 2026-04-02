import os

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, status
from fastapi.security import HTTPBearer
from models.schema.rag_schema import ChatRequest, ChatResponse
from service.rag_service import rag_service

router = APIRouter()
bearer = HTTPBearer(auto_error=False)

# 文件上传临时目录（需提前创建）
UPLOAD_DIR = "./tmp"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("chat", summary="RAG客服", response_model=ChatResponse, dependencies=[Depends(bearer)])
async def chat(req: ChatRequest, request: Request):
    user_id = request.state.user_id
    return rag_service.chat(req, user_id)


@router.post("/admin/upload/pdf", summary="PDF上传切片", dependencies=[Depends(bearer)])
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    # 1. 权限校验（仅管理员）
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    return rag_service.upload_pdf(path)
