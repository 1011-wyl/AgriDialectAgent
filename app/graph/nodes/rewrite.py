"""
Query Rewrite 节点 —— 改写用户查询以提高召回率

例如:
- "东北那个苞米" → "东北方言 苞米 玉米"
- "俺们那嘎达种地用的词" → "农业方言 种地术语"
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from app.config.settings import settings


# ==================== LLM ====================
rewrite_llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
    temperature=0.1,
)

# ==================== Prompt ====================
REWRITE_PROMPT = PromptTemplate(
    template="""你是农业搜索查询改写专家。将用户口语化的方言查询改写为更精准的检索关键词。

## 改写规则
1. 提取核心名词和方言词汇
2. 补充可能的标准化术语同义词
3. 保持简洁，不超过30个字
4. 只输出改写后的查询文本，不要解释

## 用户输入
{question}

## 改写后的查询""",
    input_variables=["question"],
)


def rewrite_node(state: dict) -> dict:
    """
    Query Rewrite 节点 —— 将口语化查询改写为检索优化的关键词

    参数:
        state: AgentState 字典

    返回:
        包含 rewrite_query 的字典
    """
    query = state.get("user_query", "")

    try:
        prompt_text = REWRITE_PROMPT.format(question=query)
        result = rewrite_llm.invoke(prompt_text)
        rewritten = result.content.strip() if hasattr(result, "content") else str(result).strip()
        # 防止 LLM 输出过长
        if len(rewritten) > 80:
            rewritten = rewritten[:80]
    except Exception:
        # 失败时使用原始查询
        rewritten = query

    return {
        "rewrite_query": rewritten,
        "logs": [f"[QueryRewrite] '{query}' → '{rewritten}'"],
    }
