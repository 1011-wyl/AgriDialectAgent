"""
统一检索接口 —— 零 LangChain 依赖
- similarity: 纯 FAISS 向量相似度
- mmr: 最大边际相关性（增加结果多样性）
- hybrid: BM25 + FAISS 混合检索
"""
from enum import Enum
from typing import List

import numpy as np

from app.rag.vector_store import DocDataclass, vector_store
from app.rag.hybrid import hybrid_search
from app.config.settings import settings


class RetrievalStrategy(str, Enum):
    """检索策略枚举"""
    SIMILARITY = "similarity"   # 纯向量相似度
    MMR = "mmr"                 # 最大边际相关性
    HYBRID = "hybrid"           # BM25 + FAISS 混合


class UnifiedRetriever:
    """统一检索器 —— 封装不同检索策略"""

    def __init__(self):
        self._strategy = RetrievalStrategy.HYBRID
        self._embeddings = None

    def _get_embeddings(self):
        if self._embeddings is None:
            from app.embedding import ModelScopeEmbeddings
            self._embeddings = ModelScopeEmbeddings()
        return self._embeddings

    def search(
        self,
        query: str,
        strategy: RetrievalStrategy = None,
        k: int = None,
    ) -> List[DocDataclass]:
        """
        执行检索

        参数:
            query: 查询文本
            strategy: 检索策略
            k: 返回文档数量
        """
        strategy = strategy or self._strategy
        k = k or settings.TOP_K_RECALL

        if strategy == RetrievalStrategy.HYBRID:
            return hybrid_search(query, k=k)

        if strategy == RetrievalStrategy.MMR:
            return self._mmr_search(query, k=k)

        # 默认: 纯向量相似度
        return vector_store.similarity_search(query, k=k)

    def _mmr_search(self, query: str, k: int = None) -> List[DocDataclass]:
        """
        MMR (最大边际相关性) 检索

        在相关性和多样性之间权衡:
            MMR = argmax [λ * sim(D, Q) - (1-λ) * max(sim(D, D_selected))]
        """
        k = k or settings.TOP_K_RECALL
        fetch_k = settings.MMR_FETCH_K
        lambda_mult = settings.MMR_LAMBDA_MULT

        # 1. 先取 fetch_k 个候选
        candidates = vector_store.similarity_search_with_scores(query, k=fetch_k)
        if not candidates:
            return []

        # 2. 编码所有候选文档向量
        embeddings = self._get_embeddings()
        doc_texts = [doc.content for doc, _ in candidates]
        doc_vectors = embeddings.embed_documents(doc_texts)
        doc_vectors = np.array(doc_vectors, dtype=np.float32)
        # L2 归一化后内积 = 余弦相似度
        norms = np.linalg.norm(doc_vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        doc_vectors = doc_vectors / norms

        # 3. MMR 贪心选择
        selected = []
        selected_indices = []

        for _ in range(min(k, len(candidates))):
            best_score = -float("inf")
            best_idx = 0

            for i, (doc, sim_score) in enumerate(candidates):
                if i in selected_indices:
                    continue

                # 相关性分数
                relevance = sim_score

                # 多样性惩罚（与已选文档的最大相似度）
                diversity = 0.0
                if selected_indices:
                    max_sim = max(
                        float(np.dot(doc_vectors[i], doc_vectors[j]))
                        for j in selected_indices
                    )
                    diversity = max_sim

                mmr = lambda_mult * relevance - (1 - lambda_mult) * diversity
                if mmr > best_score:
                    best_score = mmr
                    best_idx = i

            selected.append(candidates[best_idx][0])
            selected_indices.append(best_idx)

        return selected

    def set_strategy(self, strategy: RetrievalStrategy):
        self._strategy = strategy

    @property
    def current_strategy(self) -> RetrievalStrategy:
        return self._strategy


# 全局单例
unified_retriever = UnifiedRetriever()
