from langgraph.checkpoint.memory import InMemorySaver


def init_checkpointer():
    """初始化 LangGraph 内存检查点，支持多轮对话状态持久化"""
    return InMemorySaver()
