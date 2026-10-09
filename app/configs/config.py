from re import S

from pydantic import Field , AliasChoices
from pydantic_settings import BaseSettings  , SettingsConfigDict

class Settings (BaseSettings) :
    
    """
    Load and validate environment variables from `.env`.

    - `extra="ignore"` lets `.env` keep legacy keys (`POSTGRES_URI`, `REDIS_URL`,
    old Groq keys, etc.) without failing startup.
    - Required fields raise a clear validation error at import time if missing.
    
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    #-------------------JINA API KEY (embeddings + reranker) -----------#
    JINA_API_KEY : str 
    JINA_RERANK_MODEL:str = "jina-reranker-v3"
    JINA_RERANK_URL:str = "https://api.jina.ai/v1/rerank"
    #---------------QROQ API key ---------------####
    
    GROQ_API_KEY :str 
    GROQ_FALLBACK_API_KEY : str 

    # --- NEON SERVERLESS POSTGRES (LangGraph checkpointer) ---
    NEON_DB_URL :str 
    
    #---------------Gemini API-Key ------------#
    GEMINI_API_KEY :str 
    
    # --- QDRANT VECTOR DB ---
    QDRANT_CLUSTER_ENDPOINT: str = "https://bfedb5fe-294f-4631-8fe4-d347453614dd.sa-east-1-0.aws.cloud.qdrant.io" ,
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "enterprise_rag"

    # --- OBSERVABILITY ---
    
    LOGFIRE_TOKEN: str | None = None
    LOGFIRE_BASE_URL: str| None = None

    @property 
    def postgres_uri(self)-> str :
        """LangGraph Postgres checkpointer URI (Neon).
           Serverless Postgres closes idle connections, so append TCP keepalive
           options to keep the connection pool healthy between requests.
        """
        base =self.NEON_DB_URL.rstrip("/")
        keep_alive ="keepalives=1&keepalives_idle=30&keepalives_interval=10&keepalives_count=5"

        if "?" in base :
            return f"{base}&{keep_alive}"
        return f"{base}?{keep_alive}"

# Singleton used across the app.
settings = Settings()