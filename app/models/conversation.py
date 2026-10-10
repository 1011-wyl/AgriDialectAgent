"""
对话记录表 —— 存储每次用户查询和 Agent 回复
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.models.base import Base


class Conversation(Base):
    """对话记录 ORM 模型"""

    __tablename__ = "conversation"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")

    # 会话标识（同一 thread_id 属于同一个多轮对话）
    thread_id = Column(String(64), nullable=False, index=True, comment="会话线程ID")

    # 用户角色
    role = Column(String(16), nullable=False, default="user", comment="角色: user / assistant")

    # 用户原始输入
    user_query = Column(Text, nullable=False, comment="用户输入内容")

    # Agent 翻译/回复结果
    translation = Column(Text, nullable=True, comment="Agent 翻译或回复结果")

    # 意图分类结果
    intent = Column(String(32), nullable=True, comment="Router 识别的意图: translate/chat/weather/knowledge")

    # 引用来源（检索到的知识库片段）
    sources = Column(JSON, nullable=True, comment="引用的知识库来源列表")

    # Agent 执行路径（节点序列）
    execution_path = Column(JSON, nullable=True, comment="LangGraph 节点执行路径")

    # 反思结果
    reflection = Column(Text, nullable=True, comment="Reflector 反思结果")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    def __repr__(self):
        return f"<Conversation(id={self.id}, thread_id={self.thread_id}, intent={self.intent})>"
