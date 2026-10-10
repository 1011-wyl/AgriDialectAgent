"""
FAISS 向量库管理 —— 纯原生 FAISS 实现（零 LangChain 依赖）
- 构建：从 CSV 文件加载 → 自定义切分 → 向量化 → 构建 IndexFlatIP
- 加载：从磁盘加载 FAISS 索引 + 文档列表 (pickle)
- 新增：向已有向量库追加文档
- 删除：不支持 FAISS IndexFlatIP 单条删除，可标记 + 重建
- 更新：替换整个向量库
"""
import os
import csv
import pickle
import shutil
from typing import List, Optional
from dataclasses import dataclass, field

import numpy as np
import faiss

from app.embedding import ModelScopeEmbeddings
from app.config.settings import settings


# ==================== 自定文档数据结构（替代 langchain Document） ====================

@dataclass
class DocDataclass:
    """文档数据结构 —— 替代 langchain_core.documents.Document"""
    content: str                              # 文档文本内容
    metadata: dict = field(default_factory=dict)  # 元数据（row, source 等）
    doc_id: str = ""                          # 唯一标识


# ==================== 自定义文本切分器 ====================

def simple_text_splitter(
    text: str,
    chunk_size: int = 128,
    chunk_overlap: int = 10,
) -> List[str]:
    """
    简单滑动窗口文本切分（替代 LangChain CharacterTextSplitter）

    参数:
        text: 输入文本
        chunk_size: 每个块的最大字符数
        chunk_overlap: 相邻块的重叠字符数

    返回:
        切分后的文本块列表
    """
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - chunk_overlap
        if start >= text_len:
            break
    return chunks


# ==================== CSV 加载器 ====================

def load_csv_documents(csv_path: str) -> List[DocDataclass]:
    """
    从 CSV 文件加载农业方言数据（替代 LangChain CSVLoader）

    CSV 格式: dialect, standard_term, category

    参数:
        csv_path: CSV 文件路径

    返回:
        DocDataclass 列表，每个文档包含完整的 dialect+term+category 信息
    """
    docs = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            content = (
                f"dialect: {row.get('dialect', '').strip()}\n"
                f"standard_term: {row.get('standard_term', '').strip()}\n"
                f"category: {row.get('category', '').strip()}"
            )
            docs.append(DocDataclass(
                content=content,
                metadata={"row": dict(row)},
                doc_id=f"csv_{row.get('dialect', '')}_{len(docs)}",
            ))
    return docs


# ==================== FAISS 向量库管理 ====================

class FAISSVectorStore:
    """FAISS 向量库管理类 —— 使用原生 faiss-cpu"""

    def __init__(self):
        self.embeddings = ModelScopeEmbeddings()
        self._index: Optional[faiss.Index] = None
        self._documents: List[DocDataclass] = []

    # ==================== 构建 ====================

    def build_from_csv(self, csv_path: str = None):
        """
        从 CSV 文件构建新的 FAISS 向量库

        流程:
            1. csv.DictReader 加载原始数据
            2. 构建 DocDataclass 文档列表
            3. BGE 模型 Embedding → numpy 数组
            4. L2 归一化（适配 IndexFlatIP 内积 = 余弦相似度）
            5. faiss.IndexFlatIP 构建索引
            6. 持久化: faiss.write_index + pickle 保存文档列表

        参数:
            csv_path: CSV 文件路径

        返回:
            (index, documents) 元组
        """
        csv_path = csv_path or settings.RAW_DATA_PATH
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV 文件不存在: {csv_path}")

        # 1. 加载 CSV → DocDataclass 列表
        docs = load_csv_documents(csv_path)
        print(f"[RAG] 加载 {len(docs)} 条原始文档")

        # 2. 构建向量（BGE 512维）
        contents = [d.content for d in docs]
        vectors = self.embeddings.embed_documents(contents)
        vectors = np.array(vectors, dtype=np.float32)

        # 3. L2 归一化 → 内积 = 余弦相似度
        faiss.normalize_L2(vectors)

        # 4. 构建 FAISS 索引 (内积搜索)
        dim = vectors.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(vectors)
        self._documents = docs

        print(f"[RAG] 向量库构建完成，共 {self._index.ntotal} 条向量 (dim={dim})")

        # 5. 持久化
        self._save()
        return self._index, self._documents

    # ==================== 加载 ====================

    def load(self):
        """
        从磁盘加载已有向量库（内存缓存避免重复加载）

        返回:
            (index, documents) 元组
        """
        if self._index is not None:
            return self._index, self._documents

        index_path = os.path.join(settings.VECTOR_DB_PATH, "index.faiss")
        docs_path = os.path.join(settings.VECTOR_DB_PATH, "documents.pkl")

        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"向量库文件不存在: {index_path}\n请先调用 build_from_csv() 构建向量库"
            )

        self._index = faiss.read_index(index_path)
        with open(docs_path, "rb") as f:
            self._documents = pickle.load(f)

        print(f"[RAG] 向量库已加载，共 {self._index.ntotal} 条向量")
        return self._index, self._documents

    def _save(self):
        """持久化 FAISS 索引和文档列表"""
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        index_path = os.path.join(settings.VECTOR_DB_PATH, "index.faiss")
        docs_path = os.path.join(settings.VECTOR_DB_PATH, "documents.pkl")

        faiss.write_index(self._index, index_path)
        with open(docs_path, "wb") as f:
            pickle.dump(self._documents, f)

        print(f"[RAG] 向量库已保存到 {settings.VECTOR_DB_PATH}")

    # ==================== 搜索 ====================

    def similarity_search(self, query: str, k: int = 10) -> List[DocDataclass]:
        """
        向量相似度搜索（替代 LangChain FAISS.similarity_search）

        参数:
            query: 查询文本
            k: 返回前 K 个文档

        返回:
            DocDataclass 列表
        """
        index, documents = self.load()

        # 编码查询 → numpy 数组
        vec = self.embeddings.embed_query(query)
        vec = np.array([vec], dtype=np.float32)
        faiss.normalize_L2(vec)

        # FAISS 搜索
        scores, indices = index.search(vec, k)

        results = []
        for idx in indices[0]:
            if idx >= 0 and idx < len(documents):
                results.append(documents[idx])

        return results

    def similarity_search_with_scores(
        self, query: str, k: int = 10
    ) -> List[tuple]:
        """
        带分数的相似度搜索

        返回:
            (DocDataclass, score) 列表
        """
        index, documents = self.load()

        vec = self.embeddings.embed_query(query)
        vec = np.array([vec], dtype=np.float32)
        faiss.normalize_L2(vec)

        scores, indices = index.search(vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(documents):
                results.append((documents[idx], float(score)))

        return results

    # ==================== 新增 ====================

    def add_documents(self, documents: List[DocDataclass]) -> int:
        """
        增量添加文档（重建索引，因为 IndexFlatIP 不支持增量删除）

        参数:
            documents: 要追加的文档列表

        返回:
            新增后的总向量数
        """
        index, existing_docs = self.load()
        all_docs = existing_docs + documents

        # 重新编码所有文档
        contents = [d.content for d in all_docs]
        vectors = self.embeddings.embed_documents(contents)
        vectors = np.array(vectors, dtype=np.float32)
        faiss.normalize_L2(vectors)

        # 重建索引
        dim = vectors.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(vectors)
        self._documents = all_docs
        self._save()

        print(f"[RAG] 新增 {len(documents)} 条，当前共 {self._index.ntotal} 条")
        return self._index.ntotal

    # ==================== 更新 ====================

    def rebuild(self, csv_path: str = None):
        """完全重建向量库"""
        self.clear()
        return self.build_from_csv(csv_path)

    # ==================== 清空 ====================

    def clear(self):
        """清空向量库"""
        if os.path.exists(settings.VECTOR_DB_PATH):
            shutil.rmtree(settings.VECTOR_DB_PATH)
            os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        self._index = None
        self._documents = []
        print("[RAG] 向量库已清空")

    # ==================== 状态查询 ====================

    @property
    def is_loaded(self) -> bool:
        return self._index is not None

    @property
    def vector_count(self) -> int:
        if self._index is None:
            try:
                self.load()
            except FileNotFoundError:
                return 0
        return self._index.ntotal


# 全局单例
vector_store = FAISSVectorStore()
