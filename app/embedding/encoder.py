from modelscope import AutoModel, AutoTokenizer
import torch
from app.config.settings import settings

# 魔搭官方最新用法！无 Tasks.text_embedding！
class ModelScopeEmbeddings:
    def __init__(self):
        # 国内模型：BGE小向量
        self.model = AutoModel.from_pretrained(settings.EMBEDDING_MODEL)
        self.tokenizer = AutoTokenizer.from_pretrained(settings.EMBEDDING_MODEL)
        self.model.eval()  # 推理模式

    def encode(self, text):
        # 最新官方编码方式
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].numpy()
        return embedding[0].tolist()

    def embed_documents(self, texts):
        return [self.encode(t) for t in texts]

    def embed_query(self, text):
        return self.encode(text)

    def __call__(self, text):
        return self.embed_query(text)