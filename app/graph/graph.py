"""
LangGraph 图构建器 —— 组装所有节点和条件边

Graph 结构:
    START
      ↓
    Planner（LLM意图分析）
      ↓
    [条件边: route_by_intent]
      ├─ translate → QueryRewrite → Retriever → Reranker → Generator → Reflector
      │                                                                    ├─ pass → END
      │                                                                    └─ fail → QueryRewrite (loop)
      ├─ chat → Generator(direct) → END
      └─ weather/knowledge → Tools → Generator → END
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.state import AgentState
from app.graph.nodes import (
    planner_node,
    rewrite_node,
    retriever_node,
    reranker_node,
    generator_node,
    reflector_node,
    tool_node,
)
from app.graph.edges import route_by_intent, route_after_tool, should_retry


def build_graph() -> StateGraph:
    """
    构建 LangGraph 状态图

    返回:
        未编译的 StateGraph 实例
    """
    # 创建图（绑定 AgentState 类型）
    graph = StateGraph(AgentState)

    # ==================== 注册节点 ====================
    graph.add_node("planner", planner_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("reranker", reranker_node)
    graph.add_node("generator", generator_node)
    graph.add_node("reflector", reflector_node)
    graph.add_node("tools", tool_node)

    # ==================== 注册边 ====================
    # START → Planner
    graph.add_edge(START, "planner")

    # Planner → 条件路由（translate / chat / tools）
    graph.add_conditional_edges(
        "planner",
        route_by_intent,
        {
            "rewrite": "rewrite",
            "tools": "tools",
            "generator": "generator",
            "END": END,
        },
    )

    # RAG 流程: rewrite → retriever → reranker → generator → reflector
    graph.add_edge("rewrite", "retriever")
    graph.add_edge("retriever", "reranker")
    graph.add_edge("reranker", "generator")
    graph.add_edge("generator", "reflector")

    # Reflector → 条件路由（重试 / 结束）
    graph.add_conditional_edges(
        "reflector",
        should_retry,
        {
            "rewrite": "rewrite",
            "END": END,
        },
    )

    # Tools → 条件路由（有结果 → generator, 无结果 → END）
    graph.add_conditional_edges(
        "tools",
        route_after_tool,
        {
            "generator": "generator",
            "END": END,
        },
    )

    return graph


def compile_graph(checkpointer=None):
    """
    编译图并返回可执行的 LangGraph App

    参数:
        checkpointer: 检查点存储器（用于多轮对话状态持久化）

    返回:
        编译后的 LangGraph App
    """
    graph = build_graph()
    memory = checkpointer or InMemorySaver()
    return graph.compile(checkpointer=memory)
