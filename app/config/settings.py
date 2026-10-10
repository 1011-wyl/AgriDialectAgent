"""
配置中心 —— 使用 pydantic-settings 管理所有环境变量
所有配置项均可通过 .env 文件或环境变量覆盖
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """全局配置类，自动从 .env 文件加载"""

    # ==================== 模型配置 ====================
    EMBEDDING_MODEL: str = Field(
        default="BAAI/bge-small-zh-v1.5",
        description="嵌入模型名称（ModelScope）"
    )
    RERANKER_MODEL: str = Field(
        default="BAAI/bge-reranker-base",
        description="重排序模型名称（ModelScope）"
    )
    LLM_MODEL: str = Field(
        default="deepseek-chat",
        description="大语言模型名称"
    )

    # ==================== LLM API 配置（兼容 OpenAI 接口） ====================
    LLM_API_KEY: str = Field(
        default="",
        description="LLM API Key（支持 DeepSeek / DashScope / OpenAI 等）"
    )
    LLM_BASE_URL: str = Field(
        default="https://api.deepseek.com",
        description="LLM API 地址（OpenAI 兼容接口）"
    )

    # 兼容旧字段名（逐步废弃）
    @property
    def DASHSCOPE_API_KEY(self):
        return self.LLM_API_KEY

    @property
    def DASHSCOPE_BASE_URL(self):
        return self.LLM_BASE_URL

    # ==================== 路径配置 ====================
    RAW_DATA_PATH: str = Field(
        default=str(BASE_DIR / "data" / "raw" / "agri_1000.csv"),
        description="原始CSV知识库路径"
    )
    VECTOR_DB_PATH: str = Field(
        default=str(BASE_DIR / "vector_db"),
        description="FAISS 向量库持久化目录"
    )
    LOG_DIR: str = Field(
        default=str(BASE_DIR / "logs"),
        description="日志文件目录"
    )
    UPLOAD_DIR: str = Field(
        default=str(BASE_DIR / "data" / "uploads"),
        description="上传文件临时目录"
    )

    # ==================== 数据库配置 ====================
    DB_TYPE: str = Field(default="mysql", description="数据库类型: mysql / sqlite")
    DB_HOST: str = Field(default="127.0.0.1", description="MySQL 主机地址")
    DB_PORT: int = Field(default=3306, description="MySQL 端口")
    DB_USER: str = Field(default="root", description="MySQL 用户名")
    DB_PASSWORD: str = Field(default="", description="MySQL 密码")
    DB_NAME: str = Field(default="agri_dialect", description="数据库名")
    SQLITE_PATH: str = Field(default="sqlite:///./agri_dialect.db", description="SQLite 文件路径")

    @property
    def DATABASE_URL(self) -> str:
        """异步数据库连接URL（FastAPI 使用）"""
        if self.DB_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.SQLITE_PATH.replace('sqlite:///', '')}"
        from urllib.parse import quote_plus
        return (
            f"mysql+aiomysql://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """同步数据库连接URL（DDL/脚本使用）"""
        if self.DB_TYPE == "sqlite":
            return self.SQLITE_PATH
        from urllib.parse import quote_plus
        return (
            f"mysql+pymysql://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    # ==================== Redis 配置 ====================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis 连接地址"
    )
    REDIS_EMBEDDING_TTL: int = Field(
        default=3600,
        description="Embedding 缓存过期时间（秒），默认1小时"
    )
    REDIS_QUERY_TTL: int = Field(
        default=600,
        description="热点查询缓存过期时间（秒），默认10分钟"
    )
    REDIS_SESSION_TTL: int = Field(
        default=1800,
        description="Session 缓存过期时间（秒），默认30分钟"
    )

    # ==================== 检索参数 ====================
    TOP_K_RECALL: int = Field(
        default=20,
        description="FAISS 粗筛召回数量"
    )
    TOP_K_BM25: int = Field(
        default=20,
        description="BM25 召回数量"
    )
    TOP_K_RERANK: int = Field(
        default=10,
        description="重排序后保留数量"
    )
    MMR_FETCH_K: int = Field(
        default=30,
        description="MMR 候选池大小"
    )
    MMR_LAMBDA_MULT: float = Field(
        default=0.7,
        description="MMR 多样性参数（0=最大多样性, 1=最大相关性）"
    )
    HYBRID_WEIGHT_VECTOR: float = Field(
        default=0.6,
        description="Hybrid Search 中向量检索权重（BM25权重 = 1 - 此值）"
    )

    # ==================== Agent 参数 ====================
    MAX_RETRIES: int = Field(
        default=2,
        description="Reflector 不通过时的最大重试次数"
    )
    LLM_TEMPERATURE: float = Field(
        default=0.1,
        description="LLM 生成温度（越低越稳定）"
    )
    LLM_MAX_TOKENS: int = Field(
        default=512,
        description="LLM 单次最大输出 Token 数"
    )

    # ==================== 日志配置 ====================
    LOG_LEVEL: str = Field(
        default="INFO",
        description="日志级别: DEBUG / INFO / WARNING / ERROR"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        description="日志格式"
    )

    # ==================== 服务配置 ====================
    FASTAPI_HOST: str = Field(
        default="0.0.0.0",
        description="FastAPI 监听地址"
    )
    FASTAPI_PORT: int = Field(
        default=8000,
        description="FastAPI 监听端口"
    )
    STREAMLIT_PORT: int = Field(
        default=8501,
        description="Streamlit 监听端口"
    )

    # ==================== HuggingFace 镜像 ====================
    HF_ENDPOINT: str = Field(
        default="https://hf-mirror.com",
        description="HuggingFace 国内镜像"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局单例
settings = Settings()

# 初始化时设置环境变量（HuggingFace 镜像）
os.environ["HF_ENDPOINT"] = settings.HF_ENDPOINT
os.environ["HUGGINGFACE_HUB_BASE_URL"] = settings.HF_ENDPOINT

# 确保必要目录存在
settings.LOG_DIR and os.makedirs(settings.LOG_DIR, exist_ok=True)
settings.UPLOAD_DIR and os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
settings.VECTOR_DB_PATH and os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
