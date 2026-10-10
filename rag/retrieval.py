import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from modelscope import AutoModelForSequenceClassification, AutoTokenizer
import torch
from embedding.encoder import ModelScopeEmbeddings
from config import RAW_DATA_PATH, VECTOR_DB_PATH, RERANKER_MODEL, TOP_K_RECALL

# ==================== 魔搭重排器====================
class ModelScopeReranker:
    def __init__(self):
        self.model = AutoModelForSequenceClassification.from_pretrained(RERANKER_MODEL)
        self.tokenizer = AutoTokenizer.from_pretrained(RERANKER_MODEL)
        self.model.eval()

    def rerank(self, query, docs):
        pairs = [[query, doc.page_content] for doc in docs]
        inputs = self.tokenizer(pairs, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            scores = self.model(**inputs).logits.squeeze(-1).numpy()
        docs_scores = list(zip(docs, scores))
        docs_scores.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, s in docs_scores][:TOP_K_RECALL]

# ==================== 构建向量库 ====================
def build_and_save_vector_db():
    loader = CSVLoader(RAW_DATA_PATH, encoding="utf-8")
    docs = loader.load()
    splitter = CharacterTextSplitter(chunk_size=128, chunk_overlap=10)
    texts = splitter.split_documents(docs)
    embeddings = ModelScopeEmbeddings()
    db = FAISS.from_documents(texts, embeddings)
    db.save_local(VECTOR_DB_PATH)
    print("[OK] 向量库构建完成")
    return db

# ==================== 全局重排器 ====================
reranker = ModelScopeReranker()


def retrieve_and_rerank(query: str, k: int = TOP_K_RECALL):
    """FAISS 检索 + 重排序，返回最终文档列表"""
    embeddings = ModelScopeEmbeddings()
    db = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = db.similarity_search(query, k=k * 2)
    if reranker:
        docs = reranker.rerank(query, docs)
    return docs[:k]


# 保留兼容旧接口
def load_rerank_retriever():
    embeddings = ModelScopeEmbeddings()
    db = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    return db.as_retriever(search_kwargs={"k": TOP_K_RECALL * 2})