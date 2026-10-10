from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from config import LLM_MODEL, DASHSCOPE_API_KEY, TOP_K_RECALL, MAX_RETRIES
from rag.retrieval import retrieve_and_rerank


# ==================== 状态定义 ====================
class AgentState(TypedDict):
    query: str
    plan: str
    documents: list
    translation: str
    source: str
    retry_count: int
    feedback: str


# ==================== LLM ====================
llm = ChatOpenAI(
    model=LLM_MODEL,
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.1,
)

prompt = PromptTemplate(
    template="""你是农业方言翻译专家，仅根据参考资料将方言翻译成标准农业术语，不编造、不解释、不扩展。

参考资料：
{summaries}

用户方言：{question}
标准农业术语：""",
    input_variables=["summaries", "question"],
)


# ==================== 节点函数 ====================
def plan_node(state: AgentState) -> dict:
    """规划节点：记录当前任务步骤"""
    query = state["query"]
    plan_text = (
        f"任务规划：\n"
        f"1. 检索与用户方言「{query}」最相关的农业术语参考资料\n"
        f"2. 基于参考资料，将方言准确翻译为标准农业术语\n"
        f"3. 确保翻译严格依据资料，不编造、不扩展"
    )
    return {"plan": plan_text, "retry_count": state.get("retry_count", 0), "feedback": ""}


def retrieve_node(state: AgentState) -> dict:
    """检索节点：FAISS 检索 + 重排序"""
    query = state["query"]
    docs = retrieve_and_rerank(query, k=TOP_K_RECALL)
    return {"documents": docs}


def generate_node(state: AgentState) -> dict:
    """生成节点：拼接 Prompt 并调用 LLM 生成翻译"""
    query = state["query"]
    docs = state.get("documents", [])
    feedback = state.get("feedback", "")

    summaries = "\n".join(
        f"- {d.page_content}" for d in docs
    ) if docs else "暂无参考资料"

    if feedback:
        extra = f"\n[注意：上次结果被驳回 —— {feedback}，请重新翻译。]"
    else:
        extra = ""

    full_prompt = prompt.format(summaries=summaries, question=query) + extra
    try:
        result = llm.invoke(full_prompt)
        translation = result.content.strip() if hasattr(result, "content") else str(result).strip()
    except Exception:
        translation = ""

    source = docs[0].page_content[:80] if docs else ""

    return {"translation": translation, "source": source}


def reflect_node(state: AgentState) -> dict:
    """反思节点：验证翻译质量"""
    translation = state.get("translation", "")
    query = state["query"]
    retry_count = state.get("retry_count", 0)

    if not translation or not translation.strip():
        feedback = f"翻译结果为空，方言「{query}」未匹配到对应术语"
        return {"feedback": feedback, "retry_count": retry_count + 1}

    # 检查翻译是否只是复述了方言（没有真正翻译）
    if translation.strip() == query.strip():
        feedback = f"翻译结果与输入相同，未完成方言→术语转换"
        return {"feedback": feedback, "retry_count": retry_count + 1}

    return {"feedback": "", "retry_count": 0}


def should_retry(state: AgentState) -> Literal["retrieve", END]:
    """路由：决定重试还是结束"""
    feedback = state.get("feedback", "")
    retry_count = state.get("retry_count", 0)

    if feedback and retry_count < MAX_RETRIES:
        return "retrieve"
    return END


# ==================== 构建图 ====================
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("plan", plan_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("reflect", reflect_node)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "reflect")
    graph.add_conditional_edges("reflect", should_retry, {"retrieve": "retrieve", END: END})

    return graph


def compile_graph():
    """编译图并返回可执行的 app"""
    graph = build_graph()
    memory = InMemorySaver()
    return graph.compile(checkpointer=memory)
