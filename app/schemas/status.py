"""
Agent 状态查询接口 Pydantic Schema
"""
from typing import Optional
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Agent 状态响应体"""
    status: str = Field(default="running", description="服务状态: running / error")
    model: str = Field(description="当前使用的LLM模型")
    embedding_model: str = Field(description="当前使用的Embedding模型")
    reranker_model: str = Field(description="当前使用的Reranker模型")
    kb_document_count: int = Field(default=0, description="知识库文档总数")
    kb_vector_count: int = Field(default=0, description="知识库向量总数")
    uptime_seconds: Optional[float] = Field(default=None, description="服务运行时间(秒)")
    version: str = Field(default="1.0.0", description="系统版本")
