"""
知识库上传接口 Pydantic Schema
"""
from typing import Optional
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """上传响应体"""
    success: bool = Field(description="是否上传成功")
    filename: str = Field(description="上传的文件名")
    chunk_count: Optional[int] = Field(default=0, description="切分的文本块数量")
    vector_count: Optional[int] = Field(default=0, description="生成的向量数量")
    message: Optional[str] = Field(default=None, description="提示信息")
    error: Optional[str] = Field(default=None, description="错误信息")
