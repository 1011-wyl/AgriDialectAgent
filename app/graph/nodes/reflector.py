"""
Reflector 节点 —— 使用 LLM 反思翻译质量

判断标准:
1. 翻译是否准确
2. 翻译是否依据了知识库
3. 翻译是否只是复述方言（没有做真正的翻译）

输出:
- pass → 进入 END
- fail → 返回 QueryRewrite 重新检索
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from app.config.settings import settings


# ==================== LLM ====================
reflector_llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
    temperature=0.0,
)

# ==================== Prompt ====================
REFLECT_PROMPT = PromptTemplate(
    template="""你是农业方言翻译的质量审核专家。请判断以下翻译是否合格。

## 原始方言
{question}

## 参考资料
{summaries}

## 翻译结果
{translation}

## 评判标准
1. 翻译结果不能为空
2. 翻译结果不能与原始方言完全相同（必须是真正的翻译）
3. 翻译必须基于参考资料，不能编造
4. 翻译应该是标准农业术语，不能是解释性文本

## 输出格式（严格JSON）
{{
    "pass": true/false,
    "reason": "通过/不通过的原因（简短）"
}}""",
    input_variables=["question", "summaries", "translation"],
)


def reflector_node(state: dict) -> dict:
    """
    Reflector 节点 —— LLM 反思翻译质量

    参数:
        state: AgentState 字典

    返回:
        包含 reflection, reflection_pass, retry_count 的字典
    """
    query = state.get("user_query", "")
    translation = state.get("translation", "")
    docs = state.get("rerank_documents", [])
    retry_count = state.get("retry_count", 0)

    # ---- 快速规则检查 ----
    # 检查1: 翻译为空
    if not translation or not translation.strip():
        return {
            "reflection": "翻译结果为空",
            "reflection_pass": False,
            "retry_count": retry_count + 1,
            "logs": ["[Reflector] FAIL: 翻译为空"],
        }

    # 检查2: 翻译与输入完全相同
    if translation.strip() == query.strip():
        return {
            "reflection": "翻译结果与输入相同，未完成方言→术语转换",
            "reflection_pass": False,
            "retry_count": retry_count + 1,
            "logs": ["[Reflector] FAIL: 翻译与输入相同"],
        }

    # ---- LLM 深度反思 ----
    summaries = "\n".join(
        f"- {d['content']}" for d in docs[:3]
    ) if docs else "暂无参考资料"

    try:
        prompt_text = REFLECT_PROMPT.format(
            question=query,
            summaries=summaries,
            translation=translation,
        )
        result = reflector_llm.invoke(prompt_text)
        content = result.content.strip() if hasattr(result, "content") else str(result).strip()

        # 解析 JSON
        import json
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        reflection_data = json.loads(content)

        passed = reflection_data.get("pass", True)
        reason = reflection_data.get("reason", "")

    except Exception:
        # LLM 调用失败时，规则检查已通过，默认放行
        passed = True
        reason = "规则检查通过（LLM反思异常，默认放行）"

    return {
        "reflection": reason,
        "reflection_pass": passed,
        "retry_count": retry_count + 1 if not passed else 0,
        "logs": [
            f"[Reflector] {'PASS' if passed else 'FAIL'}: {reason}"
        ],
    }
