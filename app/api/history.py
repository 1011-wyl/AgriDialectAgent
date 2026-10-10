"""
聊天记录查询 API —— GET /api/history/{thread_id}
"""
from fastapi import APIRouter, HTTPException

from app.schemas.history import HistoryResponse
from app.service.history_service import get_history
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/history/{thread_id}", response_model=HistoryResponse, summary="查询聊天记录")
async def query_history(thread_id: str):
    """
    查询指定会话的聊天记录

    - **thread_id**: 会话线程ID
    """
    logger.info(f"[History] thread_id={thread_id}")

    result = get_history(thread_id)

    if result["total"] == 0:
        raise HTTPException(status_code=404, detail=f"未找到会话 {thread_id} 的记录")

    return HistoryResponse(**result)
