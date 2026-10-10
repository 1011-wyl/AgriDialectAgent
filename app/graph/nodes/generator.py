"""
Generator 节点 —— 调用 LLM 生成翻译或直接回复

支持两种模式:
- RAG 翻译: 将方言翻译为标准农业术语（有知识库上下文）
- 直接回复: 闲聊等不需要知识库的场景
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from app.config.settings import settings


# ==================== 降级策略：从知识库直接提取术语 ====================
def _fallback_extract(query: str, docs: list) -> str:
    """
    当 LLM 不可用时，从检索到的文档中直接提取标准术语

    策略优先级:
        1. 精确匹配: 文档中的 dialect 与用户输入完全相同
        2. 模糊匹配: 文档中的 dialect 包含用户输入 或 用户输入包含 dialect
        3. 取第一个文档的 standard_term 作为兜底

    参数:
        query: 用户原始输入
        docs: 检索到的文档列表 [{"content": "dialect: xxx\\nstandard_term: yyy", ...}, ...]

    返回:
        提取到的标准术语字符串，未找到返回空字符串
    """
    if not docs:
        return ""

    import re

    best_term = ""
    fuzzy_term = ""

    for doc in docs:
        content = doc.get("content", "")
        # 解析 CSV 格式的文档内容: "dialect: xxx\nstandard_term: yyy\ncategory: zzz"
        dialect_match = re.search(r"dialect:\s*(.+)", content)
        term_match = re.search(r"standard_term:\s*(.+)", content)

        if not dialect_match or not term_match:
            continue

        dialect = dialect_match.group(1).strip()
        standard_term = term_match.group(1).strip()

        # 1. 精确匹配
        if dialect == query:
            return standard_term

        # 2. 模糊匹配（双向包含）
        if query in dialect or dialect in query:
            if not fuzzy_term:
                fuzzy_term = standard_term

        # 3. 记录第一个结果作为兜底
        if not best_term:
            best_term = standard_term

    return fuzzy_term or best_term


# ==================== LLM ====================
generator_llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
    temperature=settings.LLM_TEMPERATURE,
    max_tokens=settings.LLM_MAX_TOKENS,
)

# ==================== 翻译 Prompt ====================
TRANSLATE_PROMPT = PromptTemplate(
    template="""你是农业方言翻译专家，仅根据参考资料将方言翻译成标准农业术语，不编造、不解释、不扩展。

参考资料：
{summaries}

用户方言：{question}
标准农业术语：""",
    input_variables=["summaries", "question"],
)

# ==================== 直接回复 Prompt ====================
CHAT_PROMPT = PromptTemplate(
    template="""你是农业AI助手，友好、简洁地回答用户问题。

用户：{question}
助手：""",
    input_variables=["question"],
)

# ==================== Tool 结果总结 Prompt ====================
TOOL_PROMPT = PromptTemplate(
    template="""你是农业AI助手。根据工具返回的结果，用简洁的中文回答用户。

工具结果：
{tool_result}

用户问题：{question}
回答：""",
    input_variables=["tool_result", "question"],
)


def generator_node(state: dict) -> dict:
    """
    Generator 节点 —— 根据场景选择不同的生成策略

    1. need_rag=True → 使用知识库上下文翻译方言
    2. need_tool=True → 使用工具结果生成回复
    3. 其他 → 直接 LLM 回复

    参数:
        state: AgentState 字典

    返回:
        包含 translation 或 direct_reply 的字典
    """
    query = state.get("user_query", "")
    need_rag = state.get("need_rag", False)
    need_tool = state.get("need_tool", False)
    tool_result = state.get("tool_result", "")
    docs = state.get("rerank_documents", [])

    # ---- 情况1: RAG 翻译 ----
    if need_rag and docs:
        summaries = "\n".join(
            f"- {d['content']}" for d in docs
        )
        prompt_text = TRANSLATE_PROMPT.format(summaries=summaries, question=query)
        try:
            result = generator_llm.invoke(prompt_text)
            translation = result.content.strip() if hasattr(result, "content") else str(result).strip()
        except Exception:
            translation = ""

        # ==== LLM 降级策略：LLM不可用时，直接从知识库提取标准术语 ====
        if not translation:
            translation = _fallback_extract(query, docs)

        return {
            "translation": translation,
            "direct_reply": "",
            "sources": [d["content"][:80] for d in docs[:3]],
            "logs": [f"[Generator] RAG翻译完成: {translation[:50]}"],
        }

    # ---- 情况2: Tool 结果总结 ----
    if need_tool and tool_result:
        prompt_text = TOOL_PROMPT.format(tool_result=tool_result, question=query)
        try:
            result = generator_llm.invoke(prompt_text)
            reply = result.content.strip() if hasattr(result, "content") else str(result).strip()
        except Exception:
            reply = tool_result
        return {
            "translation": "",
            "direct_reply": reply,
            "logs": [f"[Generator] Tool总结完成"],
        }

    # ---- 情况3: 直接聊天 ----
    prompt_text = CHAT_PROMPT.format(question=query)
    try:
        result = generator_llm.invoke(prompt_text)
        reply = result.content.strip() if hasattr(result, "content") else str(result).strip()
    except Exception:
        reply = f"你好！我是农业方言翻译助手，请输入农业方言我来帮你翻译。"

    return {
        "translation": "",
        "direct_reply": reply,
        "logs": [f"[Generator] 直接回复完成"],
    }
