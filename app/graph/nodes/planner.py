"""
Planner 节点 —— 使用 LLM 分析用户意图并输出结构化执行计划

输出 JSON 格式:
{
    "intent": "translate" | "chat" | "weather" | "knowledge",
    "need_rag": true | false,
    "need_tool": true | false,
    "tool_name": "weather" | "search" | "calculator" | ""
}
"""
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from app.config.settings import settings


# ==================== LLM ====================
planner_llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
    temperature=0.0,  # Planner 需要确定性输出
)

# ==================== Prompt ====================
PLANNER_PROMPT = PromptTemplate(
    template="""你是农业AI助手的任务规划器。分析用户输入并输出JSON格式的执行计划。

## 意图分类规则
- translate: 用户输入了农业方言，需要翻译成标准农业术语（如"打坷垃"、"耪地"）
- chat: 普通闲聊、问候、感谢等（如"你好"、"谢谢"）
- weather: 询问天气相关（如"今天天气怎么样"、"北京明天温度多少"）
- knowledge: 农业知识问答，需要外部搜索（如"小麦锈病怎么防治"、"复合肥和有机肥有什么区别"）

## 用户输入
{question}

## 输出格式（严格JSON，不要输出其他内容）
{{
    "intent": "<意图类型>",
    "need_rag": <检索本地知识库 true/false>,
    "need_tool": <需要调用工具 true/false>,
    "tool_name": "<工具名或空字符串>"
}}""",
    input_variables=["question"],
)


def planner_node(state: dict) -> dict:
    """
    Planner 节点 —— LLM 分析意图并决定执行路径

    参数:
        state: AgentState 字典

    返回:
        包含 intent, need_rag, need_tool, tool_name 的字典
    """
    query = state.get("user_query", "")

    # 调用 LLM 进行意图分析
    prompt_text = PLANNER_PROMPT.format(question=query)
    try:
        result = planner_llm.invoke(prompt_text)
        content = result.content.strip() if hasattr(result, "content") else str(result).strip()

        # 解析 JSON 输出
        # 处理 LLM 可能输出的 markdown 代码块
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        plan = json.loads(content)
    except (json.JSONDecodeError, Exception):
        # 解析失败时，默认走翻译流程
        plan = {
            "intent": "translate",
            "need_rag": True,
            "need_tool": False,
            "tool_name": "",
        }

    intent = plan.get("intent", "translate")
    need_rag = plan.get("need_rag", True)
    need_tool = plan.get("need_tool", False)
    tool_name = plan.get("tool_name", "")

    return {
        "intent": intent,
        "need_rag": need_rag,
        "need_tool": need_tool,
        "tool_name": tool_name,
        "logs": [f"[Planner] 意图={intent} | need_rag={need_rag} | tool={tool_name}"],
        "retry_count": 0,
        "error": "",
        "reflection_pass": False,
        "translation": "",
    }
