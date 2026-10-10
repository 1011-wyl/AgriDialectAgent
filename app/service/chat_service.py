"""
业务逻辑层 —— Service 层
负责调用 LangGraph、数据库、缓存等，编排完整业务流程
"""
import uuid
from app.graph import compile_graph

# 全局编译好的 LangGraph App（启动时编译一次）
_graph_app = None


def get_graph_app():
    """获取或初始化 LangGraph App（懒加载单例）"""
    global _graph_app
    if _graph_app is None:
        _graph_app = compile_graph()
    return _graph_app


async def process_chat(query: str, thread_id: str = None) -> dict:
    """
    处理聊天请求 —— 通过 LangGraph 执行完整的 Agent 流程

    参数:
        query: 用户输入
        thread_id: 会话线程ID（不传则新建）

    返回:
        包含翻译/回复、来源、日志等的字典
    """
    thread_id = thread_id or str(uuid.uuid4())
    app = get_graph_app()

    # 调用 LangGraph
    state = app.invoke(
        {"user_query": query},
        config={"configurable": {"thread_id": thread_id}},
    )

    return {
        "thread_id": thread_id,
        "query": query,
        "translation": state.get("translation", ""),
        "direct_reply": state.get("direct_reply", ""),
        "intent": state.get("intent", ""),
        "sources": state.get("sources", []),
        "reflection": state.get("reflection", ""),
        "execution_logs": state.get("logs", []),
        "error": state.get("error", ""),
    }
