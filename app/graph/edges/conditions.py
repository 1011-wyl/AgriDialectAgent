"""
LangGraph 条件边 —— 控制图的分支和循环逻辑
"""
from typing import Literal


def route_by_intent(state: dict) -> Literal["rewrite", "tools", "generator", "END"]:
    """
    根据 Planner 识别的意图路由到不同分支

    - translate → rewrite（走 RAG 翻译流程）
    - chat → generator（直接 LLM 回复）
    - weather / knowledge → tools（调用外部工具）
    - 其他 → generator（兜底）
    """
    intent = state.get("intent", "translate")
    need_rag = state.get("need_rag", False)
    need_tool = state.get("need_tool", False)

    if need_tool:
        return "tools"

    if need_rag:
        return "rewrite"

    # chat 或未知意图 → 直接 LLM 回复
    return "generator"


def route_after_tool(state: dict) -> Literal["generator", "END"]:
    """
    Tool 执行后的路由

    - 有工具结果 → generator（用 LLM 总结工具结果）
    - 无结果 → END
    """
    tool_result = state.get("tool_result", "")
    if tool_result:
        return "generator"
    return "END"


def should_retry(state: dict) -> Literal["rewrite", "END"]:
    """
    反思后的路由

    - 未通过 且 未超过最大重试次数 → rewrite（重新检索+生成）
    - 通过 或 已达最大重试 → END
    """
    from app.config.settings import settings

    passed = state.get("reflection_pass", False)
    retry_count = state.get("retry_count", 0)

    if not passed and retry_count < settings.MAX_RETRIES:
        return "rewrite"
    return "END"
