"""
AgentState —— LangGraph 全局共享状态

所有节点通过此 State 共享数据，避免函数参数满天飞。
每次节点返回 dict 即可部分更新 State。
"""
from typing import TypedDict, List, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """LangGraph 全局状态 Schema"""

    # ==================== 用户输入 ====================
    user_query: str
    """用户原始输入"""

    rewrite_query: str
    """改写后的查询（提升召回率）"""

    # ==================== Planner 输出 ====================
    intent: str
    """Router 识别的意图: translate / chat / weather / knowledge"""

    need_rag: bool
    """是否需要走 RAG 检索流程"""

    need_tool: bool
    """是否需要调用外部 Tool"""

    tool_name: str
    """需要调用的工具名称: weather / search / calculator"""

    tool_result: str
    """Tool 执行结果"""

    # ==================== 检索结果 ====================
    documents: List[dict]
    """FAISS 向量检索结果"""

    bm25_documents: List[dict]
    """BM25 关键词检索结果"""

    rerank_documents: List[dict]
    """重排序后的最终文档列表"""

    # ==================== 生成结果 ====================
    translation: str
    """翻译结果（农业方言 → 标准术语）"""

    direct_reply: str
    """直接 LLM 回复（非翻译场景，如闲聊）"""

    # ==================== 反思 ====================
    reflection: str
    """Reflector 反思结果文本"""

    reflection_pass: bool
    """反思是否通过"""

    # ==================== 对话历史 ====================
    messages: Annotated[list, add_messages]
    """多轮对话消息历史"""

    # ==================== 来源与日志 ====================
    sources: List[str]
    """引用的知识库来源"""

    logs: List[str]
    """节点执行日志"""

    # ==================== 控制 ====================
    retry_count: int
    """RAG 重试次数"""

    error: str
    """错误信息"""
