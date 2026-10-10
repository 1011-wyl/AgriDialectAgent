"""
数据库初始化脚本
- 创建所有表
- 首次启动时自动执行
"""
from app.models.base import Base
from app.database.session import sync_engine


def init_db():
    """创建所有 ORM 表（仅在表不存在时创建）"""
    Base.metadata.create_all(bind=sync_engine)
    print("[OK] 数据库表初始化完成")


if __name__ == "__main__":
    init_db()
