from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from models.schema.sql_schema import TextToSqlRequest, TextToSqlResponse
from service.sql_service import sql_service

router = APIRouter()
bearer = HTTPBearer(auto_error=False)


@router.post("/agent", summary="自然语言查询", response_model=TextToSqlResponse, dependencies=[Depends(bearer)])
async def agent(req: TextToSqlRequest, request: Request):
    if request.state.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    return sql_service.query(req, request.state.user_id)
