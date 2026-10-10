"""RAG 检索层 —— 零 LangChain 依赖：原生 FAISS + BM25 + Hybrid + Reranker"""
from app.rag.vector_store import (
    vector_store, FAISSVectorStore, DocDataclass,
    load_csv_documents, simple_text_splitter,
)
from app.rag.bm25 import bm25_retriever, BM25Retriever
from app.rag.hybrid import hybrid_search, reciprocal_rank_fusion
from app.rag.search import unified_retriever, UnifiedRetriever, RetrievalStrategy
from app.rag.reranker import reranker, BGEReranker

__all__ = [
    "vector_store", "FAISSVectorStore", "DocDataclass",
    "load_csv_documents", "simple_text_splitter",
    "bm25_retriever", "BM25Retriever",
    "hybrid_search", "reciprocal_rank_fusion",
    "unified_retriever", "UnifiedRetriever", "RetrievalStrategy",
    "reranker", "BGEReranker",
]
