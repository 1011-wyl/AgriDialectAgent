"""
Reranker 节点 —— 使用 BGE Reranker 对候选文档精细重排序
零 LangChain 依赖，直接使用 DocDataclass
"""
from app.rag.vector_store import DocDataclass
from app.rag.reranker import reranker
from app.config.settings import settings


def reranker_node(state: dict) -> dict:
    """
    Reranker 节点 —— 对 Retriever 返回的文档进行重排序

    参数:
        state: AgentState 字典

    返回:
        包含 rerank_documents 的字典（序列化为 dict 列表）
    """
    query = state.get("rewrite_query", "") or state.get("user_query", "")
    doc_dicts = state.get("documents", [])

    if not doc_dicts:
        return {
            "rerank_documents": [],
            "logs": ["[Reranker] 无文档需要重排序"],
        }

    # dict → DocDataclass
    docs = [
        DocDataclass(content=d["content"], metadata=d.get("metadata", {}))
        for d in doc_dicts
    ]

    # BGE Reranker 精排
    reranked = reranker.rerank(query, docs, top_k=settings.TOP_K_RERANK)

    # DocDataclass → dict（序列化给 State）
    rerank_dicts = [
        {"content": doc.content, "metadata": doc.metadata}
        for doc in reranked
    ]

    return {
        "rerank_documents": rerank_dicts,
        "logs": [f"[Reranker] 重排序完成，保留 {len(rerank_dicts)} 篇文档"],
    }
