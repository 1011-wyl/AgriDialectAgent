"""
知识库上传服务 —— 零 LangChain 依赖
使用原生 csv.DictReader + 自定义切分 + 原生 FAISS + BM25
"""
import os
from pathlib import Path

from app.rag.vector_store import vector_store, load_csv_documents
from app.rag.bm25 import bm25_retriever
from app.config.settings import settings


async def process_upload(file_content: bytes, filename: str) -> dict:
    """
    处理知识库文件上传

    流程:
        1. 保存上传文件到本地
        2. 用原生 csv.DictReader 加载 → DocDataclass 列表
        3. 重建 FAISS 向量库
        4. 重建 BM25 索引

    参数:
        file_content: 文件二进制内容
        filename: 原始文件名

    返回:
        处理结果字典
    """
    # 1. 保存文件
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename

    with open(file_path, "wb") as f:
        f.write(file_content)

    # 2. 加载文档（原生 csv.DictReader）
    try:
        docs = load_csv_documents(str(file_path))

        # 3. 重建 FAISS 向量库
        vector_store.clear()
        index, documents = vector_store.build_from_csv(str(file_path))
        vector_count = index.ntotal

        # 4. 重建 BM25 索引
        bm25_retriever.index(documents)
        bm25_retriever.save()

        return {
            "success": True,
            "filename": filename,
            "chunk_count": len(docs),
            "vector_count": vector_count,
            "message": f"知识库重建完成：{len(docs)} 条文档，{vector_count} 条向量",
        }
    except Exception as e:
        return {
            "success": False,
            "filename": filename,
            "chunk_count": 0,
            "vector_count": 0,
            "error": str(e),
        }
