"""
知识库文档查询 API —— GET /api/docs
"""
from fastapi import APIRouter, HTTPException
from app.rag.vector_store import vector_store
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Knowledge"])


@router.get("/docs", summary="查看知识库文档列表")
async def list_documents(page: int = 1, page_size: int = 20):
    """
    分页查询知识库中的文档

    - **page**: 页码（从1开始）
    - **page_size**: 每页数量
    """
    logger.info(f"[Docs] page={page}, page_size={page_size}")

    try:
        db = vector_store.load()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="知识库尚未构建")

    total = db.index.ntotal

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "message": f"知识库共 {total} 条向量",
    }

