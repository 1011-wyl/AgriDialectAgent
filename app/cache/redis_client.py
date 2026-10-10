"""
Redis 缓存客户端
- Embedding 缓存: 缓存文本→向量映射，减少重复计算
- 热点查询缓存: 缓存高频查询的翻译结果
- Session 缓存: 缓存会话状态
"""
import json
import hashlib
from typing import Optional

import redis.asyncio as aioredis
from app.config.settings import settings


class RedisClient:
    """
    Redis 缓存客户端

    使用方式:
        cache = RedisClient()
        await cache.connect()
        await cache.set_embedding("text", [0.1, 0.2, ...])
        vec = await cache.get_embedding("text")
    """

    def __init__(self):
        """初始化 Redis 连接参数"""
        self._redis: Optional[aioredis.Redis] = None
        self._url = settings.REDIS_URL

    async def connect(self):
        """建立 Redis 连接"""
        if self._redis is None:
            try:
                self._redis = await aioredis.from_url(
                    self._url,
                    encoding="utf-8",
                    decode_responses=False,
                )
                await self._redis.ping()
                print(f"[Redis] 连接成功: {self._url}")
            except Exception as e:
                print(f"[Redis] 连接失败（将跳过缓存）: {e}")
                self._redis = None

    async def disconnect(self):
        """关闭 Redis 连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    # ==================== Embedding 缓存 ====================

    def _embedding_key(self, text: str) -> str:
        """生成 Embedding 缓存键"""
        h = hashlib.md5(text.encode()).hexdigest()
        return f"emb:{h}"

    async def get_embedding(self, text: str) -> Optional[list]:
        """获取文本的缓存 Embedding"""
        if not self._redis:
            return None
        key = self._embedding_key(text)
        data = await self._redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_embedding(self, text: str, vector: list):
        """缓存文本的 Embedding"""
        if not self._redis:
            return
        key = self._embedding_key(text)
        await self._redis.setex(
            key,
            settings.REDIS_EMBEDDING_TTL,
            json.dumps(vector),
        )

    # ==================== 查询缓存 ====================

    async def get_query_cache(self, query: str) -> Optional[str]:
        """获取热点查询的翻译缓存"""
        if not self._redis:
            return None
        key = f"query:{query}"
        data = await self._redis.get(key)
        return data.decode() if data else None

    async def set_query_cache(self, query: str, result: str):
        """缓存查询结果"""
        if not self._redis:
            return
        key = f"query:{query}"
        await self._redis.setex(key, settings.REDIS_QUERY_TTL, result)

    # ==================== Session 缓存 ====================

    async def get_session(self, thread_id: str) -> Optional[dict]:
        """获取会话状态"""
        if not self._redis:
            return None
        key = f"session:{thread_id}"
        data = await self._redis.get(key)
        return json.loads(data) if data else None

    async def set_session(self, thread_id: str, state: dict):
        """保存会话状态"""
        if not self._redis:
            return
        key = f"session:{thread_id}"
        await self._redis.setex(
            key,
            settings.REDIS_SESSION_TTL,
            json.dumps(state, ensure_ascii=False),
        )


# 全局单例
redis_client = RedisClient()
