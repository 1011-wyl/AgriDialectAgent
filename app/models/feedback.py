"""
用户反馈表 —— 记录用户对翻译结果的质量评价
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.models.base import Base


class Feedback(Base):
    """用户反馈 ORM 模型"""

    __tablename__ = "feedback"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")

    # 关联的对话记录ID
    conversation_id = Column(Integer, nullable=False, index=True, comment="关联的对话ID")

    # 评分（1-5星）
    rating = Column(Integer, nullable=True, comment="评分: 1-5")

    # 反馈内容
    comment = Column(Text, nullable=True, comment="用户反馈文本")

    # 反馈类型
    feedback_type = Column(
        String(32), default="rating",
        comment="反馈类型: rating(评分) / correction(纠错) / suggestion(建议)"
    )

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    def __repr__(self):
        return f"<Feedback(id={self.id}, rating={self.rating}, type={self.feedback_type})>"
