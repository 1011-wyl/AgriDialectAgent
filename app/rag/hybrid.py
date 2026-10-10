"""
Hybrid Search —— 混合检索（零 LangChain 依赖）
- BM25（关键词匹配）+ FAISS（语义向量）各自检索
- RRF（Reciprocal Rank Fusion）融合排序
"""
from typing import List

from app.rag.vector_store import DocDataclass, vector_store
from app.rag.bm25 import bm25_retriever
from app.config.settings import settings


def reciprocal_rank_fusion(
    vector_results: List[DocDataclass],
    bm25_results: List[tuple],
    k: int = 60,
    weight_vector: float = None,
) -> List[DocDataclass]:
    """
    RRF 融合算法

    公式: RRF_score(d) = Σ (weight_r / (k + rank_r(d)))

    参数:
        vector_results: FAISS 检索结果
        bm25_results: BM25 检索结果 [(DocDataclass, score), ...]
        k: 平滑参数（默认 60）
        weight_vector: 向量检索权重（默认 0.6）

    返回:
        融合排序后的 DocDataclass 列表
    """
    weight_vector = weight_vector or settings.HYBRID_WEIGHT_VECTOR
    weight_bm25 = 1.0 - weight_vector

    scores = {}
    doc_map = {}

    # FAISS 贡献（rank 从 1 开始）
    for rank, doc in enumerate(vector_results, start=1):
        key = doc.content[:120]
        scores[key] = scores.get(key, 0.0) + weight_vector / (k + rank)
        doc_map[key] = doc

    # BM25 贡献
    for rank, (doc, _) in enumerate(bm25_results, start=1):
        key = doc.content[:120]
        scores[key] = scores.get(key, 0.0) + weight_bm25 / (k + rank)
        doc_map[key] = doc

    sorted_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [doc_map[key] for key in sorted_keys]


def hybrid_search(query: str, k: int = None) -> List[DocDataclass]:
    """
    混合检索: FAISS + BM25 → RRF 融合

    参数:
        query: 查询文本
        k: 返回文档数量

    返回:
        DocDataclass 列表
    """
    k = k or settings.TOP_K_RECALL

    # 1. FAISS 向量检索
    vector_docs = vector_store.similarity_search(query, k=k * 2)

    # 2. BM25 关键词检索（不可用时降级为纯 FAISS）
    try:
        bm25_docs = bm25_retriever.search(query, k=k * 2)
    except (RuntimeError, FileNotFoundError):
        return vector_docs[:k]

    # 3. RRF 融合
    fused = reciprocal_rank_fusion(vector_docs, bm25_docs)
    return fused[:k]
