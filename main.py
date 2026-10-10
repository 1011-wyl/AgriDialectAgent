"""
AgriDialectAgent 控制台入口
用法: python main.py
"""
import sys
import uuid

# 确保项目根目录在 Python 路径中
sys.path.insert(0, ".")

from app.rag.vector_store import vector_store
from app.rag.bm25 import bm25_retriever
from app.graph import compile_graph


def init_knowledge_base():
    """初始化知识库: FAISS 向量库 + BM25 索引"""
    # FAISS
    try:
        vector_store.load()
        print(f"[OK] FAISS 已加载 ({vector_store.vector_count} 条向量)")
    except:
        print("[..] FAISS 未构建，正在自动构建...")
        index, documents = vector_store.build_from_csv()
        print(f"[OK] FAISS 构建完成 ({index.ntotal} 条向量)")

    # BM25
    try:
        bm25_retriever.load()
        print(f"[OK] BM25 索引已加载")
    except:
        print("[..] BM25 未构建，正在自动构建...")
        from app.rag.vector_store import load_csv_documents
        from app.config.settings import settings
        docs = load_csv_documents(settings.RAW_DATA_PATH)
        bm25_retriever.index(docs)
        bm25_retriever.save()
        print(f"[OK] BM25 构建完成 ({len(docs)} 篇文档)")


def main():
    print("=" * 50)
    print("  AgriDialectAgent - 农业方言智能翻译")
    print("=" * 50)

    # 初始化知识库
    print()
    init_knowledge_base()

    # 编译 LangGraph
    print("\n[..] 初始化 Agent...")
    app = compile_graph()
    print("[OK] Agent 就绪!")
    print("\n输入农业方言获取标准术语，输入 exit 退出")

    thread_id = str(uuid.uuid4())

    while True:
        try:
            user_input = input("\n请输入农业方言: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Bye!")
            break

        # 执行 LangGraph
        print("[..] 处理中...", end="\r")
        state = app.invoke(
            {"user_query": user_input},
            config={"configurable": {"thread_id": thread_id}},
        )

        # 输出结果
        translation = state.get("translation", "")
        direct_reply = state.get("direct_reply", "")
        feedback = state.get("reflection", "")
        intent = state.get("intent", "")
        logs = state.get("logs", [])

        # 显示执行路径
        for log in logs:
            print(f"  {log}")

        # 显示结果
        if translation:
            print(f">> 标准农业术语: {translation}")
        elif direct_reply:
            print(f">> {direct_reply}")
        elif feedback:
            print(f">> 未找到匹配术语 ({feedback})")
        else:
            print(f">> 未找到对应术语，请检查输入是否为有效农业方言")

        # 显示来源
        sources = state.get("sources", [])
        if sources:
            print(f"  来源: {sources[0][:80]}")


if __name__ == "__main__":
    main()
