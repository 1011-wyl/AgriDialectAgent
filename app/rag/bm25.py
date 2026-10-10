"""
BM25 关键词检索器 —— 纯原生实现（零 LangChain 依赖）
- 基于 jieba 中文分词
- rank_bm25.BM25Okapi 算法
- 用于 Hybrid Search 的词汇匹配分支
"""
import os
import pickle
from typing import List, Tuple

import jieba
from rank_bm25 import BM25Okapi

from app.rag.vector_store import DocDataclass
from app.config.settings import settings


class BM25Retriever:
    """BM25 检索器 —— 基于关键词的词频-逆文档频率检索"""

    def __init__(self):
        self._bm25: BM25Okapi = None
        self._documents: List[DocDataclass] = None
        self._cache_path = os.path.join(settings.VECTOR_DB_PATH, "bm25_index.pkl")

    def _tokenize(self, text: str) -> List[str]:
        """jieba 中文分词"""
        return list(jieba.cut(text))

    def index(self, documents: List[DocDataclass]):
        """
        使用文档列表构建 BM25 索引

        参数:
            documents: DocDataclass 对象列表
        """
        self._documents = documents
        tokenized = [self._tokenize(doc.content) for doc in documents]
        self._bm25 = BM25Okapi(tokenized)
        print(f"[BM25] 索引构建完成，共 {len(documents)} 篇文档")

    def search(self, query: str, k: int = None) -> List[Tuple[DocDataclass, float]]:
        """
        检索与查询最相关的 k 篇文档

        返回:
            (DocDataclass, bm25_score) 列表，按分数降序
        """
        k = k or settings.TOP_K_BM25

        if self._bm25 is None:
            try:
                self.load()
            except FileNotFoundError:
                raise RuntimeError("BM25 索引未构建且磁盘无缓存")

        tokens = self._tokenize(query)
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(
            zip(self._documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:k]

    def save(self, path: str = None):
        """持久化 BM25 索引"""
        path = path or self._cache_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump((self._bm25, self._documents), f)
        print(f"[BM25] 索引已保存到 {path}")

    def load(self, path: str = None):
        """从磁盘加载 BM25 索引"""
        path = path or self._cache_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"BM25 索引文件不存在: {path}")
        with open(path, "rb") as f:
            self._bm25, self._documents = pickle.load(f)
        print(f"[BM25] 索引已加载，共 {len(self._documents)} 篇文档")

    @property
    def is_ready(self) -> bool:
        return self._bm25 is not None


# 全局单例
bm25_retriever = BM25Retriever()
