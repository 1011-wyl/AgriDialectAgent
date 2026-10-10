"""
Agent 状态查询 API —— GET /api/status
"""
import time
from fastapi import APIRouter

from app.schemas.status import StatusResponse
from app.config.settings import settings
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/api", tags=["Status"])

# 服务启动时间
START_TIME = time.time()


@router.get("/status", response_model=StatusResponse, summary="查询Agent运行状态")
async def agent_status():
    """
    查询 Agent 运行状态

    返回当前使用的模型、知识库大小、服务运行时间等。
    """
    vector_count = 0
    try:
        db = vector_store.load()
        vector_count = db.index.ntotal
    except Exception:
        pass

    uptime = time.time() - START_TIME

    return StatusResponse(
        status="running",
        model=settings.LLM_MODEL,
        embedding_model=settings.EMBEDDING_MODEL,
        reranker_model=settings.RERANKER_MODEL,
        kb_document_count=vector_count,
        kb_vector_count=vector_count,
        uptime_seconds=round(uptime, 1),
        version="1.0.0",
    )
