"""
聊天接口 Pydantic Schema —— 请求/响应模型
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求体"""
    query: str = Field(
        ...,
        description="用户输入的农业方言或问题",
        examples=["打坷垃", "东北那嘎达的苞米是啥意思"],
        min_length=1,
        max_length=500,
    )
    thread_id: Optional[str] = Field(
        default=None,
        description="会话线程ID（不传则自动创建新会话）",
    )


class SourceItem(BaseModel):
    """知识库来源项"""
    content: str = Field(description="文档片段内容")
    metadata: Optional[dict] = Field(default=None, description="文档元数据")


class ChatResponse(BaseModel):
    """聊天响应体"""
    thread_id: str = Field(description="会话线程ID")
    query: str = Field(description="用户原始输入")
    translation: Optional[str] = Field(default=None, description="翻译结果")
    direct_reply: Optional[str] = Field(default=None, description="直接回复（非翻译场景）")
    intent: Optional[str] = Field(default=None, description="识别的意图")
    sources: Optional[List[str]] = Field(default=None, description="引用的知识库来源")
    reflection: Optional[str] = Field(default=None, description="反思结果")
    execution_logs: Optional[List[str]] = Field(default=None, description="Agent 执行日志")
    error: Optional[str] = Field(default=None, description="错误信息")


class StreamingChunk(BaseModel):
    """Streaming 响应块"""
    event: str = Field(description="事件类型: token / node_start / node_end / done")
    data: str = Field(description="事件数据")
