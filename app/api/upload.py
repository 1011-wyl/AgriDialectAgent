"""
知识库上传 API —— POST /api/upload
"""
from fastapi import APIRouter, UploadFile, File

from app.schemas.upload import UploadResponse
from app.service.upload_service import process_upload
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Knowledge"])


@router.post("/upload", response_model=UploadResponse, summary="上传知识库CSV文件")
async def upload_knowledge(file: UploadFile = File(..., description="CSV知识库文件")):
    """
    上传知识库接口

    - 支持 CSV 格式
    - 自动解析、Embedding、重建 FAISS 和 BM25 索引
    - 覆盖已有知识库
    """
    logger.info(f"[Upload] filename={file.filename}")

    content = await file.read()
    result = await process_upload(content, file.filename)
    return UploadResponse(**result)
