"""
Tool 节点 —— 调用外部工具（天气、搜索、计算器）

当前实现为模拟版本，可替换为真实 API 调用。
"""
from app.tools.weather import get_weather
from app.tools.search import web_search
from app.tools.calculator import calculate


def tool_node(state: dict) -> dict:
    """
    Tool 调用节点 —— 根据 tool_name 调用对应的工具

    参数:
        state: AgentState 字典

    返回:
        包含 tool_result 的字典
    """
    tool_name = state.get("tool_name", "")
    query = state.get("user_query", "")

    tool_result = ""

    if tool_name == "weather":
        tool_result = get_weather(query)

    elif tool_name == "search":
        tool_result = web_search(query)

    elif tool_name == "calculator":
        tool_result = calculate(query)

    else:
        tool_result = f"未知工具: {tool_name}"

    return {
        "tool_result": tool_result,
        "logs": [f"[Tool:{tool_name}] 执行完成"],
    }
