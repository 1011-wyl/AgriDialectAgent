"""
FastAPI 中间件
- 请求耗时统计
- 访问日志记录
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger


class TimingMiddleware(BaseHTTPMiddleware):
    """
    请求耗时统计中间件

    在每个请求处理前后记录时间，计算耗时并写入日志。
    """

    async def dispatch(self, request: Request, call_next):
        """拦截请求，记录耗时"""
        start_time = time.time()

        # 记录请求
        logger.info(f"[API] {request.method} {request.url.path}")

        # 执行请求
        response = await call_next(request)

        # 计算耗时
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"[API] {request.method} {request.url.path} - {duration_ms:.1f}ms")

        # 添加自定义响应头
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.1f}"
        return response
