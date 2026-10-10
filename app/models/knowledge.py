"""
知识库表 —— 记录上传的知识库文件信息
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.models.base import Base


class Knowledge(Base):
    """知识库 ORM 模型"""

    __tablename__ = "knowledge"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")

    # 文件名
    filename = Column(String(255), nullable=False, comment="上传的文件名")

    # 文件路径
    file_path = Column(String(512), nullable=False, comment="文件存储路径")

    # 分块数量
    chunk_count = Column(Integer, default=0, comment="文档分块数量")

    # 向量数
    vector_count = Column(Integer, default=0, comment="生成的向量数量")

    # 状态
    status = Column(
        String(32), default="active",
        comment="状态: active(启用) / processing(处理中) / error(异常)"
    )

    # 错误信息
    error_msg = Column(Text, nullable=True, comment="处理异常时的错误信息")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<Knowledge(id={self.id}, filename={self.filename}, status={self.status})>"
