"""
Retriever 节点 —— 执行混合检索（BM25 + FAISS + RRF 融合）
零 LangChain 依赖，直接使用原生 DocDataclass
"""
from app.rag import hybrid_search
from app.config.settings import settings


def retriever_node(state: dict) -> dict:
    """
    Retriever 节点 —— 混合检索

    使用 rewrite_query（优先），否则使用原始 user_query

    参数:
        state: AgentState 字典

    返回:
        包含 documents 的字典（documents 为 dict 列表，适配 State 序列化）
    """
    query = state.get("rewrite_query", "") or state.get("user_query", "")

    # 执行 Hybrid Search → 返回 DocDataclass 列表
    docs = hybrid_search(query, k=settings.TOP_K_RECALL)

    # 序列化为 dict（LangGraph State 不存复杂对象）
    doc_dicts = [
        {"content": doc.content, "metadata": doc.metadata}
        for doc in docs
    ]

    return {
        "documents": doc_dicts,
        "logs": [f"[Retriever] 混合检索返回 {len(doc_dicts)} 篇文档"],
    }
