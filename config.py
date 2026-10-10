import os

# 彻底屏蔽国外
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HUGGINGFACE_HUB_BASE_URL"] = "https://hf-mirror.com"

# ==================== 路径 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data/raw/agri_1000.csv")
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data/vector_db")

# ==================== 纯国内模型（魔搭）====================
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
RERANKER_MODEL = "BAAI/bge-reranker-base"  # 国内重排模型
LLM_MODEL = "qwen-turbo"

# ==================== LLM API Key ====================
# 从环境变量读取，避免将真实密钥写入源码或提交到版本库。
DASHSCOPE_API_KEY = os.getenv("LLM_API_KEY", "")

# 检索参数
TOP_K_RECALL = 10
TOP_K_RERANK = 3

# LangGraph 反思重试上限
MAX_RETRIES = 2
