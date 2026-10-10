"""
Agent 执行日志表 —— 记录每次请求中每个节点的执行情况
用于性能监控和问题排查
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from app.models.base import Base


class AgentLog(Base):
    """Agent 执行日志 ORM 模型"""

    __tablename__ = "agent_log"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")

    # 会话标识
    thread_id = Column(String(64), nullable=False, index=True, comment="会话线程ID")

    # 节点名称
    node_name = Column(String(64), nullable=False, comment="LangGraph 节点名称")

    # 输入摘要
    input_summary = Column(Text, nullable=True, comment="节点输入摘要（截断）")

    # 输出摘要
    output_summary = Column(Text, nullable=True, comment="节点输出摘要（截断）")

    # 执行耗时（毫秒）
    duration_ms = Column(Float, nullable=True, comment="节点执行耗时(ms)")

    # 状态
    status = Column(String(16), default="success", comment="执行状态: success / error")

    # 错误信息
    error_msg = Column(Text, nullable=True, comment="异常信息")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    def __repr__(self):
        return f"<AgentLog(id={self.id}, node={self.node_name}, duration={self.duration_ms}ms)>"
