"""
AgriDialectAgent —— FastAPI 主入口
基于 FastAPI + LangGraph + RAG 的农业方言智能语义转换系统
"""
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.database.init_db import init_db
from app.utils.logger import logger
from app.utils.middleware import TimingMiddleware

# 导入所有路由
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.history import router as history_router
from app.api.status import router as status_router
from app.api.docs import router as docs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期管理

    启动时: 初始化数据库、加载向量库
    关闭时: 清理资源
    """
    # ---- 启动 ----
    logger.info("=" * 50)
    logger.info("AgriDialectAgent 启动中...")
    logger.info(f"LLM: {settings.LLM_MODEL}")
    logger.info(f"Embedding: {settings.EMBEDDING_MODEL}")
    logger.info(f"Database: {settings.DATABASE_URL}")

    # 初始化数据库表
    init_db()
    logger.info("数据库表初始化完成")

    # 预热向量库（自动构建——零 LangChain 依赖）
    from app.rag.vector_store import vector_store
    from app.rag.bm25 import bm25_retriever
    try:
        vector_store.load()
        logger.info(f"向量库已加载，共 {vector_store.vector_count} 条向量")
    except FileNotFoundError:
        logger.warning("向量库不存在，正在自动构建...")
        try:
            index, documents = vector_store.build_from_csv()
            logger.info(f"向量库构建完成，共 {index.ntotal} 条向量")
            # 同步构建 BM25
            bm25_retriever.index(documents)
            bm25_retriever.save()
            logger.info(f"BM25 索引构建完成，共 {len(documents)} 篇文档")
        except Exception as e:
            logger.error(f"向量库构建失败: {e}")

    logger.info(f"API 文档: http://{settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}/docs")
    logger.info("=" * 50)

    yield

    # ---- 关闭 ----
    logger.info("AgriDialectAgent 已关闭")


# ==================== 创建 FastAPI App ====================
app = FastAPI(
    title="AgriDialectAgent",
    description="基于 FastAPI + LangGraph + RAG 的农业方言智能语义转换系统",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ==================== 注册中间件 ====================
app.add_middleware(TimingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 注册路由 ====================
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(history_router)
app.include_router(status_router)
app.include_router(docs_router)


# ==================== 根路径 ====================
@app.get("/", summary="系统信息")
async def root():
    """根路径 —— 返回系统基本信息"""
    return {
        "name": "AgriDialectAgent",
        "version": "1.0.0",
        "description": "农业方言智能语义转换系统",
        "docs": "/docs",
        "status": "/api/status",
    }


# ==================== 直接启动 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=True,
    )
