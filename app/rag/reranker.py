"""
ModelScope BGE Reranker 封装
- 基于 BAAI/bge-reranker-base 交叉编码器
- 对候选文档进行精细重排序
"""
import torch
from modelscope import AutoModelForSequenceClassification, AutoTokenizer

from app.config.settings import settings


class BGEReranker:
    """
    BGE 交叉编码重排序器

    工作流程：
        1. 将 (query, doc) 拼接输入交叉编码器
        2. 模型输出相关性分数
        3. 按分数降序排列文档
    """

    def __init__(self):
        """加载 BGE Reranker 模型"""
        self.model = AutoModelForSequenceClassification.from_pretrained(
            settings.RERANKER_MODEL,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            settings.RERANKER_MODEL,
        )
        self.model.eval()

    def rerank(self, query: str, documents: list, top_k: int = None):
        """
        对文档列表进行重排序

        参数:
            query: 用户查询文本
            documents: 待排序的 DocDataclass 列表（含 .content 属性）
            top_k: 返回前 K 个文档，默认使用配置值

        返回:
            按相关性降序排列的 DocDataclass 列表
        """
        top_k = top_k or settings.TOP_K_RERANK

        if not documents:
            return []

        # 构建 (query, doc) 对（适配 DocDataclass.content）
        pairs = [[query, doc.content] for doc in documents]

        # 交叉编码器推理
        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        with torch.no_grad():
            scores = self.model(**inputs).logits.squeeze(-1).numpy()

        # 处理单个文档的情况
        if scores.ndim == 0:
            scores = [float(scores)]

        # 按分数降序排序
        docs_scores = list(zip(documents, scores))
        docs_scores.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in docs_scores[:top_k]]


# 全局单例（模块加载时实例化，避免重复加载模型）
reranker = BGEReranker()
