"""
聊天记录查询接口 Pydantic Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ConversationItem(BaseModel):
    """单条对话记录"""
    id: int = Field(description="记录ID")
    thread_id: str = Field(description="会话线程ID")
    role: str = Field(description="角色: user / assistant")
    user_query: str = Field(description="用户输入")
    translation: Optional[str] = Field(default=None, description="翻译/回复结果")
    intent: Optional[str] = Field(default=None, description="意图分类")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")


class HistoryResponse(BaseModel):
    """历史查询响应体"""
    thread_id: str = Field(description="会话线程ID")
    total: int = Field(description="记录总数")
    conversations: List[ConversationItem] = Field(default_factory=list, description="对话记录列表")
