"""
SQLAlchemy 声明式基类
所有 ORM 模型必须继承此类
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """ORM 基类"""
    pass
