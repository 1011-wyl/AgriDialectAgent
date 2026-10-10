"""
数据库会话管理 —— MySQL + SQLAlchemy
- 同步引擎：pymysql 驱动，用于建表等操作
- 异步引擎：aiomysql 驱动，用于 FastAPI 异步接口
- get_db：FastAPI 依赖注入
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import settings


# ==================== 同步引擎（DDL / 脚本） ====================
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=False,
    pool_pre_ping=True,           # 连接前心跳检测
    pool_size=5,                  # 连接池大小
    max_overflow=10,              # 超出 pool_size 的最大连接数
    pool_recycle=3600,            # 连接回收时间（秒）
)

# 同步会话工厂
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

# ==================== 异步引擎（FastAPI） ====================
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_sync_session() -> Session:
    """获取同步数据库会话（用于工具脚本/建表）"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入：获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session
