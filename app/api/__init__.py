"""API 路由层"""
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.history import router as history_router
from app.api.status import router as status_router
from app.api.docs import router as docs_router

__all__ = ["chat_router", "upload_router", "history_router", "status_router", "docs_router"]
